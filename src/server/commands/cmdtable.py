from src.utils.exceptions import BaseException

class DuplicateCommandException(BaseException):
    """
    Raised when a command is added whose name or alias is already represented in
    the command table.
    """
    pass


class CommandTable(object):
    """
    The command handler defers command lookups to CommandTable instances.
    These store references to various Command instances, their names and
    aliases.

    :attr dict _commands: The master command dict. The keys are the command's
        full names. The values are an instance of a Command sub-class.
    :attr dict _aliases: Similar to :attr:`_commands`, but the keys are command
        aliases and the values are references to the full entry in
        :attr:`_commands`.
    """
    def __init__(self, mud_service):
        """
        :param MudService mud_service: The MudService class running the game.
        """
        self._commands = {}
        self._aliases = {}

    def add_command(self, command):
        """
        Adds a command to the command table.

        :param Command command: The command to add.
        :raises: :class:`DuplicateCommandException` when a duplicate command
            name or alias is encountered when trying to add this command.
        """
        if self._commands.has_key(command.name):
            msg = "Attempting to add command with name %s, but an entry in "\
                  "the table with this name already exists." % command.name
            raise DuplicateCommandException(msg)
        
        self._commands[command.name] = command

        for alias in command.aliases:
            if self._aliases.has_key(alias):
                msg = "Attempting to add command with alias %s, but an entry "\
                      "in the table with this alias already exists." % alias
                raise DuplicateCommandException(msg)

            self._aliases[alias] = command

    def lookup_command(self, parsed_command):
        """
        Given a :class:`commands.parser.ParsedCommand` instance, lookup and
        return the matching command in this command table. If no matches are
        found, return ``None``.

        :param ParsedCommand parsed_command: The ParsedCommand to attempt
            to match against.
        :returns: A reference to a ``BaseCommand`` child instance, or ``None``.
        """
        name_match = self.match_name(parsed_command.command_str)
        if name_match:
            return name_match

        alias_match = self.match_alias(parsed_command.command_str)
        if alias_match:
            return alias_match

        # No matches.
        return None

    def match_name(self, name):
        """
        Given a name, return the matching ``BaseCommand`` reference, or
        ``None`` if no matches are found.

        :returns: The matching command, or ``None``.
        """
        return self._commands.get(name)

    def match_alias(self, alias):
        """
        Given a name, return the matching ``BaseCommand`` reference, or
        ``None`` if no matches are found.

        :returns: The matching command, or ``None``.
        """
        return self._aliases.get(alias)