import couchdb
from couchdb.http import ResourceNotFound

from settings import DATABASES
from src.utils import logger
from src.server.accounts.exceptions import AccountNotFoundException

class PlayerAccount(object):
    """
    This class abstracts accounts out, and is specific to the
    InMemoryAccountStore backend.
    """
    def __init__(self, **kwargs):
        """
        :param dict kwargs: All accounts are instantiated with the values from
            the DB as kwargs. Since the DB representation of all of an
            account attributes is just a dict, this works really well.
        """
        if kwargs.has_key('username'):
            kwargs['_id'] = kwargs.pop('username')

        # This stores all of the account's data.
        self.odata = kwargs

    def __getattr__(self, name):
        """
        If the user requests an attribute that can't be found on an account,
        assume they're looking for an attribute.

        :param str name: The attribute the user is looking for.
        :returns: The requested value, pulled from :attrib:`odata`.
        :raises: AttributeError if no match is found in :attrib:`odata`.
        """
        if self.odata.has_key(name):
            return self.odata[name]

        raise AttributeError()

    def get_username(self):
        return self.odata['_id']
    def set_username(self, username):
        self.odata['_id'] = username
    username = property(get_username, set_username)


class InMemoryAccountStore(object):
    """
    Serves as an in-memory store for all account values.
    """
    def __init__(self, db_name=None):
        """
        :param str db_name: Overrides the DB name for the account DB.
        """
        # Reference to CouchDB server connection.
        self._server = couchdb.Server()
        # Eventually contains a CouchDB reference. Queries come through here.
        self._db = None
        # Keys are config keys, values are config values.
        self._accounts = {}
        # Loads or creates+loads the CouchDB database.
        self._prep_db(db_name=db_name)
        # Loads all config values into RAM from CouchDB.
        self._load_accounts_into_ram()

    def _prep_db(self, db_name=None):
        """
        Sets the :attr:`_db` reference. Creates the CouchDB if the requested
        one doesn't exist already.

        :param str db_name: Overrides the DB name for the account DB.
        """
        if not db_name:
            # Use the default configured DB name for config DB.
            db_name = DATABASES['accounts']['NAME']

        try:
            # Try to get a reference to the CouchDB database.
            self._db = self._server[db_name]
        except ResourceNotFound:
            logger.warning('No DB found, creating a new one.')
            self._db = self._server.create(db_name)

    def _load_accounts_into_ram(self):
        """
        Loads all of the config values from the DB into RAM.
        """
        for doc_id in self._db:
            username = doc_id
            doc = self._db[username]
            # Retrieves the JSON doc from CouchDB.
            self._accounts[username.lower()] = PlayerAccount(**doc)

    def save_account(self, account_or_username):
        """
        Saves an account to CouchDB. The odata attribute on each account is
        the raw dict that gets saved to and loaded from CouchDB.
        """
        odata = account_or_username.odata
        username = odata['_id'].lower()
        self._db.save(odata)
        self._accounts[username] = account_or_username

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
