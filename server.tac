"""
This module implements the main dott server process, the core of the
game engine. No telnet goofery is handled here, that is the domain of the
proxy server.

The server listens for an AMP connection from the proxy, which allows for
two-way communication between proxy and MUD server. This allows either the MUD
or the proxy to go up and down without the other really caring.
"""
import time

from twisted.application import internet, service

import settings
from src.server.protocols.proxyamp import AmpServerFactory
from src.game.commands.global_cmdtable import GlobalCommandTable
from src.server.commands.handler import CommandHandler
from src.server.objects.in_memory_store import InMemoryObjectStore

class MudService(service.Service):
    """
    The main server service task.
    """
    def __init__(self):
        # Holds the TCP services.
        self.service_collection = None
        self.game_running = True

        self.proxyamp = None

        # Global command table. This is consulted  by the command handler
        # when users send input.
        self.global_cmd_table = GlobalCommandTable(self)

        # The command handler takes user input and figures out what to do
        # with it. This typically results in a command from a command table
        # being ran.
        self.command_handler = CommandHandler(self)

        # The object store holds instances of all of the game's objects. It
        # directs loading all objects from the DB at start time, and has some
        # convenience method for finding and retrieving objects during
        # runtime.
        self.object_store = InMemoryObjectStore(self)
        
        # All of the instantiations above just prep data structures. The
        # following lines do all of the loading.
        self.object_store._prepare_at_load()

        # Begin startup debug output.
        print('\n' + '-' * 50)

        self.start_time = time.time()

        # Make output to the terminal. 
        print(' %s started on port(s):' % settings.GAME_NAME)
        print('  * %s' % settings.SERVER_AMP_PORT)
        print('-'*50)

    def start_services(self, app_to_start):
        """
        Starts all of the TCP services.
        """
        self.service_collection = service.IServiceCollection(app_to_start)

        amp_factory = AmpServerFactory(self)

        port = settings.SERVER_AMP_PORT
        amp_server = internet.TCPServer(port, amp_factory)
        amp_server.setName('dott%s' % port)
        amp_server.setServiceParent(self.service_collection)

            
# Putting it all together
application = service.Application('dott_server')
mud_service = MudService()
mud_service.start_services(application)