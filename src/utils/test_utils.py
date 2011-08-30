import unittest2
from src.game.commands.global_cmdtable import GlobalCommandTable
from src.server.commands.handler import CommandHandler
from src.server.accounts.in_memory_store import InMemoryAccountStore
from src.server.objects.in_memory_store import InMemoryObjectStore
from src.server.sessions.session_manager import SessionManager

class MockMudService(object):
    """
    Mocks up the MudService class found in dott.tac.
    """
    def __init__(self):
        self.global_cmd_table = None
        self.command_handler = None
        self.session_manager = None
        self.object_store = None
        self.account_store = None

        self.global_cmd_table = GlobalCommandTable(self)
        self.command_handler = CommandHandler(self)
        self.session_manager = SessionManager(self)
        self.object_store = InMemoryObjectStore(self, db_name='dott_objects_test')
        self.account_store = InMemoryAccountStore(self, db_name='dott_accounts_test')

        self.object_store._prepare_at_load()

class DottTestCase(unittest2.TestCase):
    """
    Some helpers for unit testing.
    """
    def setUp(self):
        """
        By default, create a bare minimal set of data stores.
        """
        self.create_clean_game_env()

    def tearDown(self):
        """
        Delete the created data stores between unit tests.
        """
        self.cleanup_game_env()

    def create_clean_game_env(self):
        """
        Creates a fresh set of stores, DBs, and etc.
        """
        self.mud_service = MockMudService()
        self.global_cmd_table = self.mud_service.global_cmd_table
        self.command_handler = self.mud_service.command_handler
        self.session_manager = self.mud_service.session_manager
        self.object_store = self.mud_service.object_store
        self.account_store = self.mud_service.account_store

    def cleanup_game_env(self):
        """
        Cleans up the created environment.
        """
        del self.object_store._server['dott_objects_test']
        del self.account_store._server['dott_accounts_test']