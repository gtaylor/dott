"""
This module contains classes related to Sessions. sessionhandler has the things
needed to manage them.
"""
from twisted.conch.telnet import StatefulTelnetProtocol

from mongomud.src.server.session import Session
from mongomud.src.utils import logger
from mongomud.src.utils.general import to_unicode, to_str

class MudTelnetProtocol(StatefulTelnetProtocol):
    """
    This class represents a player's session. Each player
    gets a session assigned to them whenever
    they connect to the game server. All communication
    between game and player goes through here. 
    """
    def __str__(self):
        return "MudTelnetProtocol conn from %s" % self.getClientAddress()[0]
        
    def connectionMade(self):
        """
        What to do when we get a connection.
        """
        self.session = Session(self)
        logger.info('New connection from: %s' % self.getClientAddress()[0])
        self.session.show_game_connect_screen()

    def getClientAddress(self):
        """
        Returns the client's address and port in a tuple. For example
        ('127.0.0.1', 41917)
        """
        return self.transport.client

    def disconnectClient(self):
        """
        Manually disconnect the client.
        """
        self.transport.loseConnection()

    def connectionLost(self, reason):
        """
        Execute this when a client abruplty loses their connection.
        """
        logger.info('Disconnected: %s' % self)
        self.handle_close()
        
    def lineReceived(self, raw_string):
        """
        Communication Player -> Evennia
        Any line return indicates a command for the purpose of the MUD.
        So we take the user input and pass it to the Player and their currently
        connected character.
        """
        try:
            raw_string = to_unicode(raw_string)
        except Exception, e:
            self.sendLine(str(e))
            return 
        #self.execute_cmd(raw_string)
        self.session.msg("ECHO: %s" % raw_string)        

    def msg(self, message):
        """
        Communication Evennia -> Player        
        """
        try:
            message = to_str(message)
        except Exception, e:
            self.sendLine(str(e))
            return 
        self.sendLine(message)
            
    def handle_close(self):
        """
        Break the connection and do some accounting.
        """            
        self.disconnectClient()
        self.logged_in = False  
    