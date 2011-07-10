class ParsedCommand(object):
    """
    A parsed command, broken up into something the command handler can
    muddle through.
    """
    pass

class CommandParser(object):
    """
    Parses user input. Dices it up into bits that the command handler can
    look through to figure out what gets done.
    """
    def parse(self, command_str):
        """
        Do the magic. Returns

        :param str command_str: The command string to parse.
        """
        pass