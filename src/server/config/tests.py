from src.utils.test_utils import DottTestCase
from src.server.config.defaults import DEFAULTS
from src.server.config.exceptions import ConfigParamNotFound

class InMemoryConfigStoreTests(DottTestCase):
    def test_basic(self):
        """
        Loads the config vals into RAM and makes sure they match the defaults.
        """
        idle_timeout = self.config_store.get_value('IDLE_TIMEOUT')
        self.assertEqual(idle_timeout, DEFAULTS['IDLE_TIMEOUT'])

        # Update config value.
        self.config_store.set_value('IDLE_TIMEOUT', 3601)

        # Check to see if the config value updated.
        idle_timeout = self.config_store.get_value('IDLE_TIMEOUT')
        self.assertEqual(idle_timeout, 3601)

    def test_invalid_params(self):
        """
        Tests invalid get/set config values.
        """
        self.assertRaises(ConfigParamNotFound, self.config_store.get_value, 'BLARTY')
        self.assertRaises(ConfigParamNotFound, self.config_store.set_value, 'BLARTY', 1)