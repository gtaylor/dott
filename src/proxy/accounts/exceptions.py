from src.utils.exceptions import BaseException

class AccountNotFoundException(BaseException):
    """
    Raise this when the user tries to query for an account that does not exist.
    """
    pass

class UsernameTakenException(BaseException):
    """
    Raise this when someone attempts to create an account with a username
    that is already taken.
    """
    pass