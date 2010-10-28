"""
This module contains classes related to Sessions. sessionhandler has the things
needed to manage them.
"""
import time
from datetime import datetime

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
        # setup the parameters
        self.session = Session(self)
        # send info
        logger.info('New connection from: %s' % self.getClientAddress()[0])        
        # add this new session to handler
        #sessionhandler.add_session(self)
        # show a connect screen 
        self.session.game_connect_screen()

    def getClientAddress(self):
        """
        Returns the client's address and port in a tuple. For example
        ('127.0.0.1', 41917)
        """
        return self.transport.client

    def prep_session(self):
        """
        This sets up the main parameters of
        the session. The game will poll these
        properties to check the status of the
        connection and to be able to contact
        the connected player. 
        """
        # main server properties 
        self.server = self.factory.server
        self.address = self.getClientAddress()

        # player setup 
        self.name = None
        self.uid = None
        self.logged_in = False

        # The time the user last issued a command.
        self.cmd_last = time.time()
        # Player-visible idle time, excluding the IDLE command.
        self.cmd_last_visible = time.time()
        # Total number of commands issued.
        self.cmd_total = 0
        # The time when the user connected.
        self.conn_time = time.time()
        #self.channels_subscribed = {}

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
      
    def update_counters(self, idle=False):
        """
        Hit this when the user enters a command in order to update idle timers
        and command counters. If silently is True, the public-facing idle time
        is not updated.
        """
        # Store the timestamp of the user's last command.
        self.cmd_last = time.time()
        if not idle:
            # Increment the user's command counter.
            self.cmd_total += 1
            # Player-visible idle time, not used in idle timeout calcs.
            self.cmd_last_visible = time.time()
            
    def handle_close(self):
        """
        Break the connection and do some accounting.
        """            
        self.disconnectClient()
        self.logged_in = False  
    