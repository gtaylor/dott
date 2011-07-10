"""
Sessionhandler, stores and handles a list of all player sessions.
"""
import time

from src.utils import logger
import settings

class SessionManager(object):
    # Our list of connected sessions.
    SESSIONS = []
    
    @classmethod
    def add_session(cls, session):
        """
        Adds a session to the session list.
        """
        cls.SESSIONS.append(session)
        logger.info('Sessions active: %d' % len(cls.get_sessions(return_unlogged=True)))
    
    @classmethod
    def get_sessions(cls, return_unlogged=False):
        """
        Lists the connected session objects.
        """
        if return_unlogged:
            return cls.SESSIONS
        else:
            return [sess for sess in cls.SESSIONS if sess.logged_in]

    @classmethod 
    def disconnect_all_sessions(cls):
        """
        Cleanly disconnect all of the connected sessions.
        """
        for sess in cls.get_sessions():
            sess.handle_close()
    
    @classmethod
    def check_all_sessions(cls):
        """
        Check all currently connected sessions and see if any are dead.
        """
        idle_timeout = int(settings.IDLE_TIMEOUT)
    
        if idle_timeout <= 0:
            return
    
        if len(cls.SESSIONS) <= 0:
            return
        
        for sess in cls.get_sessions(return_unlogged=True):
            if (time.time() - sess.cmd_last) > idle_timeout:
                sess.msg("Idle timeout exceeded, disconnecting.")
                sess.handle_close()

    @classmethod
    def remove_session(cls, session):
        """
        Removes a session from the session list.
        """
        try:
            cls.SESSIONS.remove(session)
            logger.info('Sessions active: %d' % len(cls.get_sessions()))
        except ValueError:        
            # the session was already removed.
            logger.info("Unable to remove session: %s" % session)
            return 
    
    @classmethod
    def announce_all(cls, message):
        """
        Announces something to all connected players.
        """
        for session in cls.get_sessions():
            session.msg('%s' % message)