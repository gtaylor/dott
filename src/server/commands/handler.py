from src.server.commands.parser import CommandParser
from src.server.commands.exceptions import CommandError

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

    @property
    def command_table(self):
        """
        Returns a reference to the global CommandTable instance. Go through
        a property to avoid reference counting, which would mess up code reload.

        :rtype: :class:`src.game.commands.global_cmdtable.GlobalCommandTable`
        :returns: A reference to the global command table instance.
        """
        return self._mud_service.global_cmd_table

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
        result = self.command_table.lookup_command(parsed_command)
        if result:
            try:
                result.func(invoker, parsed_command)
            except CommandError, exc:
                invoker.emit_to(exc.message)
            except:
                invoker.emit_to('ERROR: A critical error has occured.')
                raise

            return result

        # No command match.
        return None

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
            return cmd_match

        # No matches, show the "Huh?".
        return None