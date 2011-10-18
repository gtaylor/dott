"""
Parent loader related exceptions.
"""
from src.utils.exceptions import BaseException

class InvalidParent(BaseException):
    """
    Raised when attempting to load or use a parent that doesn't exist.
    """
    pass