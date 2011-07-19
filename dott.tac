"""
This module implements the main dott server process, the core of the
game engine. 
"""
import time

from twisted.application import internet, service
from twisted.internet import protocol, reactor

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

        # Global command table. This is consulted  by the command handler
        # when users send input.
        from src.game.commands.global_cmdtable import GlobalCommandTable
        self.global_cmd_table = GlobalCommandTable()

        # The command handler takes user input and figures out what to do
        # with it. This typically results in a command from a command table
        # being ran.
        from src.server.commands.handler import CommandHandler
        self.command_handler = CommandHandler(
            command_table=self.global_cmd_table,
        )

        # The config store is a really basic key/value store used to get/set
        # configuration values. This can be things like an idle timeouts,
        # new player starting rooms, and etc. This varies from the 'settings'
        # module, which only contains low-level server configuration values
        # that can't go in the config store.
        from src.server.config.in_memory_store import InMemoryConfigStore
        self.config_store = InMemoryConfigStore()

        # The session manager tracks all connections. Think of this as a list
        # of who is currently playing.
        from src.server.sessions.session_manager import SessionManager
        self.session_manager = SessionManager(
            config_store=self.config_store,
        )

        # The object store holds instances of all of the game's objects. It
        # directs loading all objects from the DB at start time, and has some
        # convenience method for finding and retrieving objects during
        # runtime.
        from src.server.objects.in_memory_store import InMemoryObjectStore
        self.object_store = InMemoryObjectStore(
            config_store=self.config_store,
            command_handler=self.command_handler,
            session_manager=self.session_manager,
        )

        # The account store holds account data like usernames, emails, and
        # encrypted passwords. This is primarily used to log users in.
        from src.server.accounts.in_memory_store import InMemoryAccountStore
        self.account_store = InMemoryAccountStore(
            object_store=self.object_store,
        )

        # Have to set this after account store initialization, since both
        # objects refer to one another, but we can't instantiate them at the
        # same time.
        self.object_store._account_store = self.account_store

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
            server = internet.TCPServer(port, factory)
            server.setName('dott%s' % port)
            server.setServiceParent(self.service_collection)

            
# Twisted requires us to define an 'application' attribute.
application = service.Application('dott')
# The main mud service. Import this for access to the server methods.
mud_service = MudService()
mud_service.start_services(application)
