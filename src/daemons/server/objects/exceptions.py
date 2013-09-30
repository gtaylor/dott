"""
Object store related exceptions.
"""

from src.utils.exceptions import BaseException


class NoSuchObject(BaseException):
    """
    Raised when an object ID is provided, but no match was found in the
    object store.
    """

    pass