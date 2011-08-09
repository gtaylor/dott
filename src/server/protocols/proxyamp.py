"""
Contains the protocols, commands, and client factory needed for the server
to service the MUD proxy.
"""
from twisted.protocols import amp
from twisted.internet import protocol

class AmpServerFactory(protocol.ServerFactory):
    """
    This factory creates new ProxyAMP protocol instances to use for accepting
    connections from TCPServer.
    """
    def __init__(self, server):
        """
        :attr ProxyService _mud_service: The global :class:`MudService` instance.
        :attr ProxyAMP protocol: The protocol the factory creates instances of.
        """
        self._mud_service = server
        self.protocol = ProxyAMP

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


class Echo(amp.Command):
    arguments = [('value', amp.String())]
    response = [('value', amp.String())]


class SendThroughObjectCmd(amp.Command):
    """
    AMP command for sending player input from the proxy to the MUD server.
    """
    arguments = [
        ('object_id', amp.Unicode()),
        ('input', amp.Unicode()),
    ]
    response = []


class ProxyAMP(amp.AMP):
    """
    This is the protocol that the MUD server and the proxy server
    communicate to each other with. AMP is a bi-directional protocol, so
    both the proxy and the MUD use the same commands and protocol.

    Each valid command has a public method on this class, and specifies
    a responder, which is an amp.Command sub-class. The responder class
    dictates data types for arguments and response.
    """
    def send_through_object_command(self, object_id, input):
        print "OBJECT", object_id
        print "INPUT", input
        service = self.factory._mud_service
        print service
        obj = service.object_store.get_object(object_id)
        print "RUNNING ON", obj
        obj.execute_command(input)
        return {}
    SendThroughObjectCmd.responder(send_through_object_command)

    def echo(self, value):
        print 'Echo:', value
        print 'Factory', self.factory.server
        return {'value':value}
    Echo.responder(echo)