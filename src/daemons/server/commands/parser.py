class ParsedCommand(object):
    """
    A parsed command, broken up into something the command handler can
    muddle through.

    :attr str command_str: The command that was passed.
    :attr list switches: Switches that were passed in with the command.
    :attr list arguments: A list of strings representing the arguments passed
        with the command.
    """
    def __init__(self, command_str, switches, arguments):
        self.command_str = command_str
        self.switches = switches
        self.arguments = arguments

class CommandParser(object):
    """
    Parses user input. Dices it up into bits that the command handler can
    look through to figure out what gets done.
    """
    def parse(self, raw_input):
        """
        Do the magic. Returns the parsed command in a convenient container
        object for use by the command handler.

        :param str raw_input: The raw input string to parse.
        :rtype: :class:`ParsedCommand`
        """
        if raw_input[0] == ':':
            raw_input = raw_input.replace(':', 'emote ', 1)
        elif raw_input[0] == ';':
            raw_input = raw_input.replace(';', 'emote/nospace ', 1)

        tokens = raw_input.split()
        # The first word should be the command string.
        command_str = tokens[0]
        # Switches are separated by forward slash.
        command_str_split = command_str.split('/')
        # First element (0) is the command string, everything after that
        # is a switch.
        switches = command_str_split[1:]
        # Go back and re-set this to exclude any switches that were in the
        # original command_str.
        command_str = command_str_split[0]
        # Anything after the first word is considered an argument.
        arguments = tokens[1:]

        return ParsedCommand(command_str, switches, arguments)