"""
Interactive shells are best thought of interactive menus. All user input is
intercepted and piped through the InteractiveShell, instead of going through
the command parser/handler, though you can still manually use the command
parser if you need it.
"""
class InteractiveShell(object):
    """
    Sub-classes of this class should be set on the
    :class:`src.server.sessions.session.Session` object's
    :attr:`interactive_shell` attribute. This causes all input to be piped
    through this class's :meth:`process_input` method.
    """
    def __init__(self, session):
        """
        :attr Session session: A reference back to the Session object that
            instantiated this shell object.
        """
        self.session = session

    def process_input(self, user_input):
        """
        All user input gets pipied through this method when an interactive
        shell is set on the Session.

        :param str user_input: The raw input from the user.
        """
        raise NotImplementedError('Implement process_input().')

    def end_shell(self):
        """
        Ends the interactive shell by un-setting the
        :class:`src.server.sessions.session.Session` object's
        :attr:`interactive_shell` attribute.
        """
        self.session.interactive_shell = None