import couchdb
from couchdb.http import ResourceNotFound

import settings
from src.utils import logger
from src.server.protocols.proxyamp import CreatePlayerObjectCmd
from src.proxy.accounts.exceptions import AccountNotFoundException, UsernameTakenException
from src.proxy.accounts.account import PlayerAccount

class InMemoryAccountStore(object):
    """
    Serves as an in-memory store for all account values.
    """
    def __init__(self, mud_service, db_name=None):
        """
        :param MudService mud_service: The MudService class running the game.
        :keyword str db_name: Overrides the DB name for the account DB.
        """
        self._mud_service = mud_service

        # Reference to CouchDB server connection.
        self._server = couchdb.Server()
        # Eventually contains a CouchDB reference. Queries come through here.
        self._db = None
        # Keys are usernames, values are PlayerAccount instances.
        self._accounts = {}
        # Loads or creates+loads the CouchDB database.
        self._prep_db(db_name=db_name)
        # Loads all PlayerAccount objects into RAM from CouchDB.
        self._load_accounts_into_ram()

    @property
    def _object_store(self):
        """
        Short-cut to the global object store.

        :rtype: InMemoryObjectStore
        :returns: Reference to the global object store instance.
        """
        return self._mud_service.object_store

    def _prep_db(self, db_name=None):
        """
        Sets the :attr:`_db` reference. Creates the CouchDB if the requested
        one doesn't exist already.

        :param str db_name: Overrides the DB name for the account DB.
        """
        if not db_name:
            # Use the default configured DB name for config DB.
            db_name = settings.DATABASES['accounts']['NAME']
        try:
            # Try to get a reference to the CouchDB database.
            self._db = self._server[db_name]
        except ResourceNotFound:
            logger.warning('No DB found, creating a new one.')
            self._db = self._server.create(db_name)

    def _load_accounts_into_ram(self):
        """
        Loads all of the PlayerAccount instances from the DB into RAM.
        """
        for doc_id in self._db:
            username = doc_id
            doc = self._db[doc_id]
            # Retrieves the JSON doc from CouchDB.
            self._accounts[username.lower()] = PlayerAccount(
                self._mud_service,
                **doc
            )

    def create_account(self, username, password, email):
        """
        Creates and returns a new account. Makes sure the username is unique.

        :param str username: The username of the account to create.
        :param str password: The raw (un-encrypted) password.
        :rtype: :class:`PlayerAccount`
        :returns: The newly created account.
        :raises: :class:`UsernameTakenException` if someone attempts to create
            a duplicate account.
        """
        if self._accounts.has_key(username.lower()):
            raise UsernameTakenException('Username already taken.')

        # Tells the mud server to create a new PlayerObject to go with the
        # eventual new PlayerAccount. Returns a deferred, which we add
        # a callback for and handle in obj_created_callback.
        p_obj_created_deferred = self._mud_service.proxyamp.callRemote(
            CreatePlayerObjectCmd,
            username=username,
        )

        def obj_created_callback(results):
            """
            This is ran once the mud server creates a new PlayerObject. The
            proxy then creates a matching PlayerAccount, set to controlling
            the newly created PlayerObject.

            :param str object_id: The newly created PlayerObject on the
                mud server.
            """
            # Create the PlayerAccount, pointed at the PlayerObject's _id.
            account = PlayerAccount(
                self._mud_service,
                _id=username,
                email=email,
                currently_controlling_id=results['object_id'],
                password=None,
            )
            # Hashes the password for safety.
            account.set_password(password)
            account.save()
        p_obj_created_deferred.addCallback(obj_created_callback)

    def save_account(self, account):
        """
        Saves an account to CouchDB. The _odata attribute on each account is
        the raw dict that gets saved to and loaded from CouchDB.

        :param PlayerAccount account: The account to save.
        """
        odata = account._odata
        username = odata['_id'].lower()
        self._db.save(odata)
        self._accounts[username] = account

    def get_account(self, username):
        """
        Retrieves the requested :class:`PlayerAccount` instance.

        :param str username: The username of the account to retrieve.
        :rtype: :class:`PlayerAccount`
        :returns: The requested account.
        """
        try:
            return self._accounts[username.lower()]
        except KeyError:
            raise AccountNotFoundException('No such account with username "%s" found' % username)
