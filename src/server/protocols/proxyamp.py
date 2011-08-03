from twisted.protocols import amp

class Echo(amp.Command):
    arguments = [('value', amp.String())]
    response = [('value', amp.String())]

class ProxyAMP(amp.AMP):

    def echo(self, value):
        print 'Echo:', value
        print 'Factory', self.factory.server
        return {'value':value}
    Echo.responder(echo)