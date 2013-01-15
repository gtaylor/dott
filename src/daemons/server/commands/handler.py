from src.daemons.server.commands.parser import CommandParser
from src.daemons.server.commands.exceptions import CommandError

class CommandHandler(object):
    """
    This class takes incoming user input, parses it, and figures out what to
    do. The destination is typically a command of some sort.

    :attr CommandTable command_table: The global command table that all
        input gets checked against. Other command tables may get checked, but
        this one is always looked at.
    :attr CommandParser command_parser: The command parser to use in order to
        break raw input into useful components.
    """
    def __init__(self, mud_service):
        """
        :param MudService mud_service: The MudService class running the game.
        """
        self._mud_service = mud_service
        self.parser = CommandParser()
        self.global_command_table = self._mud_service.global_cmd_table
        self.global_admin_command_table = self._mud_service.global_admin_cmd_table

    def _match_user_input_to_exit(self, invoker, parsed_command):
        """
        Attempts to match the user's input to an exit.

        :rtype: ``ExitObject`` or ``None``
        :returns: The first exit match, or ``None`` if there were no matches.
        """
        if not invoker.location:
            return None

        # This is what we'll match aliases against.
        exit_str = parsed_command.command_str.lower()

        # Contents of current location = neighbors.
        exit_neighbors = [obj for obj in invoker.location.get_contents() \
                             if obj.base_type == 'exit']

        # This is pretty inefficient.
        for exit in exit_neighbors:
            for alias in exit.aliases:
                alias = alias.lower()
                if alias == exit_str:
                    # Match found.
                    return exit

        # No exit match.
        return None

    def _match_user_input_to_command(self, invoker, parsed_command):
        """
        Attempts to match the user's input to a command.

        :rtype: ``BaseCommand`` or ``None``
        :returns: The BaseCommand sub-class that matched the user's input,
            or ``None`` if no match was found.
        """
        # Default to no match.
        result = None

        # Local admin table, but only if it exists and invoker is an admin.
        if invoker.location \
           and invoker.location.local_admin_command_table \
           and invoker.is_admin():
            result = invoker.location.local_admin_command_table.lookup_command(
                parsed_command
            )

        if not result \
           and invoker.location and invoker.location.local_command_table:
            result = invoker.location.local_command_table.lookup_command(
                parsed_command
            )

        # Admin command table, but only if invoker is an admin.
        if not result and invoker.is_admin():
            result = self.global_admin_command_table.lookup_command(
                parsed_command
            )

        # Global command table.
        if not result:
            result = self.global_command_table.lookup_command(
                parsed_command
            )

        return result

    def handle_input(self, invoker, command_string):
        """
        Given string-based input, parse for command details, then send the
        result off to various command tables to attempt execution. If no match
        is found, ``None`` is returned so this may be handled at the
        a higher level.

        :param BaseObject invoker: The object generating the input.
        :param str command_string: The raw input to handle.
        :returns: The BaseCommand instance that was executed, or ``None`` if
            there was no match.
        """
        parsed_command = self.parser.parse(command_string)

        exit_match = self._match_user_input_to_exit(invoker, parsed_command)
        if exit_match:
            # Exit match was found, make this a 'go' command with the
            # argument being the exit's object id.
            parsed_command.command_str = 'go'
            # Prepend a pound sign to force an object ID lookup.
            parsed_command.arguments = ['#%s' % exit_match.id]

        cmd_match = self._match_user_input_to_command(invoker, parsed_command)
        if cmd_match:
            # We found a command match, try to run it.
            try:
                cmd_match.func(invoker, parsed_command)
            except CommandError, exc:
                # An PEBKAC type error occured within the command.
                invoker.emit_to(exc.message)
            except:
                # Something bad happened. We'll want to handle this more
                # gracefully in the future.
                # TODO: Handle this more gracefully.
                invoker.emit_to('ERROR: A critical error has occured.')
                raise

            # Everything went better than expected.
            return cmd_match

        # No matches, show the "Huh?".
        return None