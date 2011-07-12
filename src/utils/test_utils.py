import unittest2
from src.server.accounts.in_memory_store import InMemoryAccountStore
from src.server.config.in_memory_store import InMemoryConfigStore
from src.server.objects.in_memory_store import InMemoryObjectStore

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
        self.config_store = InMemoryConfigStore(
            db_name='dott_config_test')
        self.object_store = InMemoryObjectStore(
            db_name='dott_objects_test',
            config_store=self.config_store)
        self.account_store = InMemoryAccountStore(
            db_name='dott_accounts_test',
            object_store=self.object_store)

    def cleanup_game_env(self):
        """
        Cleans up the created environment.
        """
        del self.config_store._server['dott_config_test']
        del self.object_store._server['dott_objects_test']
        del self.account_store._server['dott_accounts_test']