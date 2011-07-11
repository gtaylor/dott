"""
This module contains the basic telnet protocol.
"""
from twisted.conch.telnet import StatefulTelnetProtocol

from src.utils import logger
from src.utils.general import to_unicode, to_str
from src.server.sessions.session import Session
from src.server.sessions.session_manager import SessionManager

class MudTelnetProtocol(StatefulTelnetProtocol):
    """
    This protocol class serves as the lowest level pipe between the server
    and the player. There is no game or business logic here, just
    communication-related stuff.
    """
    def __str__(self):
        return "MudTelnetProtocol conn from %s" % self.getClientAddress()[0]
        
    def connectionMade(self):
        """
        What to do when we get a connection.
        """
        self.session = Session(self)
        logger.info('New connection: %s' % self)
        self.session.show_game_connect_screen()
        SessionManager.add_session(self.session)

    def getClientAddress(self):
        """
        Returns the client's address and port in a tuple. For example
        ('127.0.0.1', 41917)
        """
        return self.transport.client

    def disconnectClient(self):
        """
        Ran when a client disconnects.
        """
        SessionManager.remove_session(self.session)
        self.transport.loseConnection()        

    def connectionLost(self, reason):
        """
        Execute this when a client abruplty loses their connection.
        """
        logger.info('Disconnected: %s' % self)
        self.disconnectClient()
        
    def lineReceived(self, raw_string):
        """
        This is fired every time the server receives a line from the client.
        This gets handed off to the command parser.

        :param str raw_string: The raw string received from the client.
        """
        try:
            raw_string = to_unicode(raw_string)
        except Exception, e:
            self.sendLine(str(e))
            return

        # Hand the input off to the command parser.
        self.session.execute_command(raw_string)

    def msg(self, message):
        """
        Sends a message to the client.

        :param str message: The message to send to the client.
        """
        try:
            message = to_str(message)
        except Exception, e:
            self.sendLine(str(e))
            return

        self.sendLine(message)
    