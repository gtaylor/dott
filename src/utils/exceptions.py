class BaseException(Exception):
    """
    Sub-class this with your custom exceptions.
    """
    def __init__(self, message, *args):
        Exception.__init__(self, message, *args)
        # The error message to show in __str__.
        self.message = message

    def __str__(self):
        return repr(self.message)