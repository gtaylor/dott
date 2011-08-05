"""
Contains the protocols, commands, and client factory needed for the server
to service the MUD proxy.
"""
from twisted.protocols import amp
from twisted.internet import protocol

class Echo(amp.Command):
    arguments = [('value', amp.String())]
    response = [('value', amp.String())]

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


class ProxyAMP(amp.AMP):
    """
    This is the protocol that the MUD server and the proxy server
    communicate to each other with. AMP is a bi-directional protocol, so
    both the proxy and the MUD use the same commands and protocol.

    Each valid command has a public method on this class, and specifies
    a responder, which is an amp.Command sub-class. The responder class
    dictates data types for arguments and response.
    """
    def echo(self, value):
        print 'Echo:', value
        print 'Factory', self.factory.server
        return {'value':value}
    Echo.responder(echo)