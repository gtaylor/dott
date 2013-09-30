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


class ObjectHasZoneMembers(BaseException):
    """
    Raised when an object being deleted or moved to a different ID would
    cause zone members to start freaking out.
    """

    pass