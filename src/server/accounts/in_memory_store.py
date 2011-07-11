import hashlib

import couchdb
from couchdb.http import ResourceNotFound

import settings
from src.utils import logger
from src.server.accounts.exceptions import AccountNotFoundException, UsernameTakenException

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
    # This just acts as an alias to self.odata['_id'].
    username = property(get_username, set_username)

    def _get_hash_for_password(self, password):
        """
        Given a password, calculate the hash value that would be stored
        in the DB. Useful for setting new passwords, or authenticating
        a login attempt by comparing calculated vs. expected hashes.

        :param str password: The password to calc a hash for.
        """
        pass_str = 'sha512:%s:%s' % (settings.SECRET_KEY, password)
        return hashlib.sha512(pass_str).hexdigest()

    def set_password(self, new_password):
        """
        Given a new password, creates the proper password hash.

        .. note:: You will still need to save this PlayerAccount after setting
            a new password for the change to take affect. Saving is done
            through :class:`InMemoryAccountStore`.

        :param str new_password: The new password to set.
        """
        self.password = self._get_hash_for_password(new_password)

    def check_password(self, password):
        """
        Given a password value, calculate its password hash and compare it to
        the value in memory/DB.

        :rtype: bool
        :returns: If the given password's hash matches what we have for the
            account, returns `True`. If not, `False.
        """
        given_hash = self._get_hash_for_password(password)
        return given_hash == self.password


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
            db_name = settings.DATABASES['accounts']['NAME']

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

        account = PlayerAccount(username=username, email=email)
        account.set_password(password)
        self.save_account(account)
        return self.get_account(username)

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
