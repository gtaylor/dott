import couchdb
from couchdb.http import ResourceNotFound

from settings import DATABASES
from src.utils import logger
from src.server.config.defaults import DEFAULTS
from src.server.config.exceptions import ConfigParamNotFound

class InMemoryConfigStore(object):
    """
    Serves as an in-memory store for all config values.
    """
    def __init__(self, mud_service, db_name=None):
        """
        :param MudService mud_service: The MudService class running the game.
        :keyword str db_name: Overrides the DB name for the config DB.
        """
        # Reference to the MudService instance that ties everything together.
        self._mud_service = mud_service
        # Reference to CouchDB server connection.
        self._server = couchdb.Server()
        # Eventually contains a CouchDB reference. Queries come through here.
        self._db = None
        # Keys are config keys, values are config values.
        self._config = {}
        # Loads or creates+loads the CouchDB database.
        self._prep_db(db_name=db_name)
        # Loads all config values into RAM from CouchDB.
        self._load_config_into_ram()

    def _prep_db(self, db_name=None):
        """
        Sets the :attr:`_db` reference. Creates the CouchDB if the requested
        one doesn't exist already.

        :param str db_name: Overrides the DB name for the config DB.
        """
        if not db_name:
            # Use the default configured DB name for config DB.
            db_name = DATABASES['config']['NAME']

        try:
            # Try to get a reference to the CouchDB database.
            self._db = self._server[db_name]
        except ResourceNotFound:
            logger.warning('No DB found, creating a new one.')
            self._db = self._server.create(db_name)

        if not len(self._db):
            # No config values are in the config DB. Saving right now causes
            # an empty document to be created.
            self._save_config()

    def _load_config_into_ram(self):
        """
        Loads all of the config values from the DB into RAM.
        """
        for doc_id in self._db:
            # Retrieves the JSON doc from CouchDB.
            self._config = self._db[doc_id]

    def _save_config(self):
        """
        Saves the config dict to CouchDB.
        """
        self._db.save(self._config)

    def get_value(self, config_param):
        """
        Returns the value for a config key.

        :param str config_param: The config key whose value to retrieve.
        :returns: The value for the config key.
        """
        if not DEFAULTS.has_key(config_param):
            raise ConfigParamNotFound('get_value: Invalid config parameter: %s' % config_param)

        return self._config.get(config_param, DEFAULTS[config_param])

    def set_value(self, config_param, config_value):
        """
        Updates a config parameter.

        :param str config_param: Which config param to update.
        :param object config_value: The new value for the param.
        """
        if not DEFAULTS.has_key(config_param):
            raise ConfigParamNotFound('set_value: Invalid config parameter: %s' % config_param)

        self._config[config_param] = config_value

        self._save_config()