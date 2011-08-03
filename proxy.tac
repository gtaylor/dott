"""
This module drives the proxy that sits in front of the MUD server. The proxy
is the only one of the two that handles Telnet connections from players.
It uses an auto-reconnect internet.TCPClient to speak to the MUD server
through the Twisted AMP protocol (a two-way async protocol).

The benefits are twofold:
  * Telnet handling is solely the domain of the proxy, and the actual MUD server
    itself is free to worry about more important things. Like the game.
  * The MUD can restart without interrupting player connections. As a result of
    this, we don't need to implement any crazy code reloading junk. We can
    just cold restart without many players even noticing.
"""
import time

from twisted.application import internet, service
from twisted.internet import protocol

import settings
from src.proxy.protocols.telnet import MudTelnetProtocol
from src.server.protocols.proxyamp import ProxyAMP, Echo

class AmpClientFactory(protocol.ReconnectingClientFactory):
    """
    This factory creates new ProxyAMP protocol instances to use to connect
    to the MUD server. It also maintains the :attr:`proxyamp` attribute
    on the :class:`ProxyService` instance, which is used for piping input
    fron Telnet to the MUD server.
    """
    # Initial reconnect delay in seconds.
    initialDelay = 1
    maxDelay = 1

    def __init__(self, server):
        """
        :attr ProxyService server: The global :class:`ProxyService` instance.
        """
        self.server = server

    def startedConnecting(self, connector):
        """
        Called when starting to try to connect to the MUD server.
        """
        print 'Started to connect.'

    def buildProtocol(self, addr):
        """
        Pops out ProxyAMP() instances. Only one should ever be in use at a
        time. This method also sets the :attr:`proxyamp` attribute
        on the :class:`ProxyService` instance, which is used for piping input
        fron Telnet to the MUD server.
        """
        print 'Connected.'
        # Bring reconnect delay back down to initial value, in case the AMP
        # connection is broken later on.
        self.resetDelay()
        # Update the MudService instance's proxyamp attribute to be the
        # currently active ProxyAMP() instance, which we can communicate
        # to the MUD server with.
        self.server.proxyamp = ProxyAMP()
        return self.server.proxyamp

    def clientConnectionLost(self, connector, reason):
        """
        Called when the AMP connection to the MUD server is lost.
        """
        print 'Lost connection.  Reason:', reason
        protocol.ReconnectingClientFactory.clientConnectionLost(
            self,
            connector,
            reason
        )

    def clientConnectionFailed(self, connector, reason):
        """
        Called when an AMP connection attempt to the MUD server fails.
        """
        print 'Connection failed. Reason:', reason
        protocol.ReconnectingClientFactory.clientConnectionFailed(
            self,
            connector,
            reason
        )

class ProxyService(service.Service):
    """
    This is the main Service class that ties the proxy together. It listens
    for telnet connections and maintains a client connection to the MUD
    server over AMP.
    """
    def __init__(self):
        """
        :attr ProxyAMP proxyamp: The currently active ProxyAMP instance.
            This can be used to communicate with the MUD server through.
        """
        self.session_manager = None
        self.account_store = None

        self.proxyamp = None

        self.start_time = time.time()

    def pipe_user_input(self, message):
        """
        Stub method to pipe user input from telnet to the MUD server.
        """
        self.proxyamp.callRemote(Echo, value=message)

    def start_services(self, app_to_start):
        """
        Starts all of the TCP services.
        """
        self.service_collection = service.IServiceCollection(app_to_start)

        telnet_factory = protocol.ServerFactory()
        telnet_factory.protocol = MudTelnetProtocol
        telnet_factory.server = self

        print('\n' + '-' * 50)
        print(' %s started on port(s):' % settings.GAME_NAME)
        for port in settings.PROXY_LISTEN_PORTS:
            telnet_server = internet.TCPServer(port, telnet_factory)
            telnet_server.setName('dott_telnet_%s' % port)
            telnet_server.setServiceParent(self.service_collection)
            print('  * %s' % port)
        print('-'*50)

        amp_client = internet.TCPClient(
            settings.SERVER_AMP_HOST,
            settings.SERVER_AMP_PORT,
            AmpClientFactory(self)
        )
        amp_client.setName('dott_amp')
        amp_client.setServiceParent(self.service_collection)

# Putting it all together.
application = service.Application('dott_proxy')
mud_service = ProxyService()
mud_service.start_services(application)
