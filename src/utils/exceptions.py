class BaseException(Exception):
    """
    Sub-class this with your custom exceptions.
    """
    def __init__(self, message, *args):
        """
        :param str message: The message to show in the exception's
            string representation.
        """
        Exception.__init__(self, message, *args)
        # The error message to show in __str__.
        #noinspection PyPropertyAccess
        self.message = message

    def __str__(self):
        return repr(self.message)