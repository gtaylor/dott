"""
This module implements the main MongoMud server process, the core of the
game engine. 
"""
import time

from twisted.application import internet, service
from twisted.internet import protocol, reactor

from mongomud import settings
from mongomud.src.server.protocols.telnet import MudTelnetProtocol
from mongomud.src.server.session_manager import SessionManager

class MudService(service.Service):
    """
    The main server service task.
    """
    def __init__(self):
        # Holds the TCP services.
        self.service_collection = None
        self.game_running = True

        # Begin startup debug output.
        print('\n' + '-' * 50)

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
        SessionManager.announce_all(message)
        SessionManager.disconnect_all_sessions()
        reactor.callLater(0, reactor.stop) #@UndefinedVariable

    def get_mud_service_factory(self):
        """
        Retrieve instances of the server
        """
        factory = protocol.ServerFactory()
        factory.protocol = MudTelnetProtocol
        factory.server = self
        return factory

    def start_services(self, app_to_start):
        """
        Starts all of the TCP services.
        """
        self.service_collection = service.IServiceCollection(app_to_start)
        for port in settings.LISTEN_PORTS:
            factory = self.get_mud_service_factory()
            mongomud_server = internet.TCPServer(port, factory) #@UndefinedVariable
            mongomud_server.setName('mongomud%s' % port)
            mongomud_server.setServiceParent(self.service_collection)

# Twisted requires us to define an 'application' attribute.
application = service.Application('mongomud')
# The main mud service. Import this for access to the server methods.
mud_service = MudService()
mud_service.start_services(application)
