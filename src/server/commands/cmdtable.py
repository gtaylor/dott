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
    def __init__(self):
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