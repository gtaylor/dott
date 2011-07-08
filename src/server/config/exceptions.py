from src.utils.exceptions import BaseException

class ConfigParamNotFound(BaseException):
    """
    Raise this when the user tries to get/set a config param that
    doesn't exist.
    """
    pass