"""
This module implements the main Evennia server process, the core of the
game engine. 
"""
import time
import sys
import os

from twisted.application import internet, service
from twisted.internet import protocol, reactor

from mongomud import settings
from mongomud.src.server.protocols.telnet import MudTelnetProtocol
from mongomud.src.utils import logger

class EvenniaService(service.Service):
    """
    The main server service task.
    """    
    def __init__(self):
        # Holds the TCP services.
        self.service_collection = None
        self.game_running = True
            
        # Begin startup debug output.
        print('\n' + '-'*50)         

        self.start_time = time.time()

        # Make output to the terminal. 
        print(' %s started on port(s):' % settings.GAME_NAME)
        for port in settings.LISTEN_PORTS:
            print('  * %s' % port)              
        print('-'*50)
    
    def shutdown(self, message=None):
        """
        Gracefully disconnect everyone and kill the reactor.
        """
        if not message:
            message = 'The server has been shutdown. Please check back soon.'

        reactor.callLater(0, reactor.stop)
        
    def getEvenniaServiceFactory(self):
        """
        Retrieve instances of the server
        """
        factory = protocol.ServerFactory()
        factory.protocol = MudTelnetProtocol
        factory.server = self
        return factory

    def start_services(self, application):
        """
        Starts all of the TCP services.
        """
        self.service_collection = service.IServiceCollection(application)
        for port in settings.LISTEN_PORTS:
            evennia_server = \
                internet.TCPServer(port, self.getEvenniaServiceFactory())
            evennia_server.setName('Evennia%s' %port)
            evennia_server.setServiceParent(self.service_collection)

# Twisted requires us to define an 'application' attribute.
application = service.Application('mongomud') 
# The main mud service. Import this for access to the server methods.
mud_service = EvenniaService()
mud_service.start_services(application)
