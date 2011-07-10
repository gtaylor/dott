"""
Contains a parent class which all commands should inherit from.
"""

class Command(object):
    """
    A command. All commands should sub-class this.

    :attr str name: The command name. IE: 'look'.
    :attr list aliases: Alternative ways to call the
        command (e.g. 'l', 'glance', 'examine').
    """
    name = None
    aliases = []