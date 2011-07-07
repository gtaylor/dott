import unittest
from src.server.config.in_memory_store import InMemoryConfigStore
from src.server.config.defaults import DEFAULTS

class InMemoryConfigStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryConfigStore(db_name='dott_config_test')

    def tearDown(self):
        del self.store._server['dott_config_test']

    def test_basic(self):
        """
        Loads the config vals into RAM and makes sure they match the defaults.
        """
        idle_timeout = self.store.get_value('IDLE_TIMEOUT')
        self.assertEqual(idle_timeout, DEFAULTS['IDLE_TIMEOUT'])