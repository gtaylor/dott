"""
Command-related related exceptions.
"""
from src.utils.exceptions import BaseException

class CommandError(BaseException):
    """
    Raised whenever there is an error in the parsing or execution of a
    player or admin's command. IE: Trying to look at something that doesn't
    exist, omitting an argument, etc.
    """
    pass