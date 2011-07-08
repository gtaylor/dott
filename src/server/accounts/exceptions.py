from src.utils.exceptions import BaseException

class AccountNotFoundException(BaseException):
    """
    Raise this when the user tries to query for an account that does not exist.
    """
    pass