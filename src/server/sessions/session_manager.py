import time

from src.utils import logger

class SessionManager(object):
    """
    This class keeps track of all of the :class:`src.server.session.Session`
    objects that are currently connected to the game.

    :attr list _sessions: The list of currently connected sessions.
    :attr InMemoryConfigStore config_store: The config store to retrieve
            settings from.
    """
    def __init__(self, mud_service):
        """
        :param MudService mud_service: The MudService class running the game.
        """
        self._mud_service = mud_service
        self._config_store = self._mud_service.config_store
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
            return [sess for sess in self._sessions if sess.logged_in]

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

        idle_timeout = int(self._config_store.get_value('IDLE_TIMEOUT'))
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
            # the session was already removed.
            logger.info("Unable to remove session: %s" % session)
            return 
    
    def announce_all(self, message):
        """
        Announces something to all connected players.
        """
        for session in self.get_sessions():
            session.msg('%s' % message)

    def get_session_for_object(self, obj):
        """
        Given an object, return the session controlling the object (if any).

        :returns: The Session or ``None`` if no match was found.
        """
        for session in self._sessions:
            controlled = session.get_controlled_object()
            # Compare based on ID.
            if controlled and controlled.id == obj.id:
                return session

        # No matches if we get to this point.
        return None