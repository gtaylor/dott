from src.server.commands.parser import CommandParser

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
    def __init__(self, command_table):
        self.parser = CommandParser()
        self.command_table = command_table

    def handle_input(self, command_string):
        """
        Given string-based input, parse for command details, then send the
        result off to various command tables to attempt execution. If no match
        is found, ``None`` is returned so this may be handled at the
        a higher level.

        :param str command_string: The raw input to handle.
        :returns: The BaseCommand instance that was executed, or ``None`` if
            there was no match.
        """
        parsed_command = self.parser.parse(command_string)

        result = self.command_table.lookup_command(parsed_command)
        if result:
            result.func(parsed_command)
            return result

        return None