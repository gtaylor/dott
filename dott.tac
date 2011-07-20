"""
This module implements the main dott server process, the core of the
game engine. 
"""
import time

from twisted.application import internet, service
from twisted.internet import protocol, reactor
import exocet

import settings
from src.server.protocols.telnet import MudTelnetProtocol

class MudService(service.Service):
    """
    The main server service task.
    """
    def __init__(self):
        # Holds the TCP services.
        self.service_collection = None
        self.game_running = True

        self.global_cmd_table = None
        self.command_handler = None
        self.config_store = None
        self.session_manager = None
        self.object_store = None
        self.account_store = None

        self.load_components()

        # Begin startup debug output.
        print('\n' + '-' * 50)

        self.start_time = time.time()

        # Make output to the terminal. 
        print(' %s started on port(s):' % settings.GAME_NAME)
        for port in settings.LISTEN_PORTS:
            print('  * %s' % port)
        print('-'*50)

    def _import_component(self, path, class_name):
        """
        Loads a component with Exocet. This allows us to do really simple
        code re-loading.

        :returns: A reference to the requested class.
        """
        mod = exocet.loadNamed(str(path), exocet.pep302Mapper)
        return getattr(mod, class_name)

    def shutdown(self, message=None):
        """
        Gracefully disconnect everyone and kill the reactor.
        """
        if not message:
            message = 'The server has been shutdown. Please check back soon.'
        SessionManager.announce_all(message)
        SessionManager.disconnect_all_sessions()
        reactor.callLater(0, reactor.stop) #@UndefinedVariable

    def load_components(self):
        """
        Loads the various components of the service. Imports and instantiates
        them, passes reference to self so the components can interact.

        TODO: Load with exocet.
        """
        # Global command table. This is consulted  by the command handler
        # when users send input.
        GlobalCommandTable = self._import_component(
            'src.game.commands.global_cmdtable',
            'GlobalCommandTable'
        )
        self.global_cmd_table = GlobalCommandTable(self)

        # The command handler takes user input and figures out what to do
        # with it. This typically results in a command from a command table
        # being ran.
        CommandHandler = self._import_component(
            'src.server.commands.handler',
            'CommandHandler'
        )
        self.command_handler = CommandHandler(self)

        # The config store is a really basic key/value store used to get/set
        # configuration values. This can be things like an idle timeouts,
        # new player starting rooms, and etc. This varies from the 'settings'
        # module, which only contains low-level server configuration values
        # that can't go in the config store.
        InMemoryConfigStore = self._import_component(
            'src.server.config.in_memory_store',
            'InMemoryConfigStore'
        )
        self.config_store = InMemoryConfigStore(self)

        # The session manager tracks all connections. Think of this as a list
        # of who is currently playing.
        SessionManager = self._import_component(
            'src.server.sessions.session_manager',
            'SessionManager'
        )
        self.session_manager = SessionManager(self)

        # The object store holds instances of all of the game's objects. It
        # directs loading all objects from the DB at start time, and has some
        # convenience method for finding and retrieving objects during
        # runtime.
        InMemoryObjectStore = self._import_component(
            'src.server.objects.in_memory_store',
            'InMemoryObjectStore'
        )
        self.object_store = InMemoryObjectStore(self)

        # The account store holds account data like usernames, emails, and
        # encrypted passwords. This is primarily used to log users in.
        InMemoryAccountStore = self._import_component(
            'src.server.accounts.in_memory_store',
            'InMemoryAccountStore'
        )
        self.account_store = InMemoryAccountStore(self)

        # All of the instantiations above just prep data structures. The
        # following lines do all of the loading.
        self.object_store._prepare_at_load()

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
            server = internet.TCPServer(port, factory)
            server.setName('dott%s' % port)
            server.setServiceParent(self.service_collection)

            
# Twisted requires us to define an 'application' attribute.
application = service.Application('dott')
# The main mud service. Import this for access to the server methods.
mud_service = MudService()
mud_service.start_services(application)
