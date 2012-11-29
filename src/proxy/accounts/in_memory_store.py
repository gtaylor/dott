import json
from txpostgres import txpostgres
from twisted.internet.defer import inlineCallbacks, returnValue

import settings
from src.proxy.accounts.on_first_run import setup_db
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

        # Keys are usernames, values are PlayerAccount instances.
        self._accounts = {}

        self._db_name = db_name or settings.DATABASE_NAME
        # This eventually contains a txpostgres Connection object, which is
        # where we can query.
        self._db = None

    @property
    def _object_store(self):
        """
        Short-cut to the global object store.

        :rtype: InMemoryObjectStore
        :returns: Reference to the global object store instance.
        """

        return self._mud_service.object_store

    @inlineCallbacks
    def prepare_at_startup(self):
        """
        Sets the :attr:`_db` reference. Does some basic DB population if
        need be.
        """

        # Just in case this is a code reload.
        self._accounts = {}
        # Instantiate the connection to Postgres.
        self._db = txpostgres.Connection()
        yield self._db.connect(
            user=settings.DATABASE_USERNAME,
            database=self._db_name
        )

        # See if the dott_objects table already exists. If not, create it.
        results = yield self._db.runQuery(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name=%s",
            (settings.ACCOUNT_TABLE_NAME,)
        )

        if not results:
            setup_db(self, self._db)
        else:
            self._load_accounts_into_ram()

    @inlineCallbacks
    def _load_accounts_into_ram(self):
        """
        Loads all of the PlayerAccount instances from the DB into RAM.
        """

        logger.info("Loading accounts into RAM.")

        results = yield self._db.runQuery("SELECT * FROM %s"% settings.ACCOUNT_TABLE_NAME)

        for username, json_str in results:
            doc = json.loads(json_str)

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

    @inlineCallbacks
    def save_account(self, account):
        """
        Saves an account to the DB. The _odata attribute on each account is
        the raw dict that gets saved to and loaded from the DB entry.

        :param PlayerAccount account: The account to save.
        """

        odata = account._odata
        username = odata['_id'].lower()

        logger.info("Saving new account")
        yield self._db.runOperation(
            """
            INSERT INTO dott_accounts (username, data) VALUES (%s, %s)
            """, (username, json.dumps(odata))
        )
        logger.info("Account saved.")

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
