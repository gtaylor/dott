import time

from src.utils import logger
import settings

class SessionManager(object):
    """
    This class keeps track of all of the :class:`src.server.session.Session`
    objects that are currently connected to the game.
    """
    def __init__(self, mud_service):
        """
        :param MudService mud_service: The MudService class running the game.
        """
        self._mud_service = mud_service
        # The list of currently connected sessions.
        self._sessions = []

    def add_session(self, session):
        """
        Adds a session to the session list.
        """
        self._sessions.insert(0, session)
        logger.info('Sessions active: %d' % len(self.get_sessions(return_unlogged=True)))

    def get_sessions(self, return_unlogged=False):
        """
        Lists the connected session objects.
        """
        if return_unlogged:
            return self._sessions
        else:
            return [sess for sess in self._sessions if sess.is_logged_in()]

    def disconnect_all_sessions(self):
        """
        Cleanly disconnect all of the connected sessions.
        """
        for sess in self.get_sessions():
            sess.handle_close()

    def check_all_sessions(self):
        """
        Check all currently connected sessions and see if any are dead.
        """
        if len(self._sessions) <= 0:
            return

        idle_timeout = settings.USER_IDLE_TIMEOUT
        if idle_timeout <= 0:
            return
        
        for sess in self.get_sessions(return_unlogged=True):
            if (time.time() - sess.cmd_last) > idle_timeout:
                sess.msg("Idle timeout exceeded, disconnecting.")
                sess.handle_close()

    def remove_session(self, session):
        """
        Removes a session from the session list.
        """
        try:
            self._sessions.remove(session)
            logger.info('Sessions active: %d' % len(self.get_sessions()))
        except ValueError:        
            # the session was already removed. Probably garbage collected.
            return 
    
    def announce_all(self, message):
        """
        Announces something to all connected players.
        """
        for session in self.get_sessions():
            session.msg('%s' % message)

    def get_sessions_for_object_id(self, obj_id):
        """
        Given an object ID, return the sessions controlling the object (if any).

        .. note:: This supports multiple sessions per object, though we
            don't allow it.

        :rtype: list
        :returns: The sessions controlling the object, if any.
        """
        sessions = []

        for session in self._sessions:
            controlling_id = session.account.currently_controlling_id
            # Compare based on ID.
            if controlling_id == obj_id:
                sessions.append(session)

        # No matches if we get to this point.
        return sessions

    def emit_to_object(self, obj_id, message):
        """
        Emits to all sessions controlling the given object ID.

        :param str obj_id: The object whose sessions to emit to.
        :param str message: The message to emit.
        """
        sessions = self.get_sessions_for_object_id(obj_id)
        for session in sessions:
            session.msg(message)