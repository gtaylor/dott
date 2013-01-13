from twisted.internet.defer import inlineCallbacks, returnValue

from src.proxy.accounts.db_io import DBManager
from src.server.protocols.proxyamp import CreatePlayerObjectCmd
from src.proxy.accounts.exceptions import AccountNotFoundException, UsernameTakenException
from src.proxy.accounts.account import PlayerAccount


class InMemoryAccountStore(object):
    """
    Serves as an in-memory store for all account values.
    """

    def __init__(self, proxy_service, db_name=None):
        """
        :param ProxyService proxy_service: The Twisted service class that
            runs the proxy.
        :keyword str db_name: Overrides the DB name for the account DB.
        """

        # TODO: This should be _proxy_service.
        self._mud_service = proxy_service

        # Keys are usernames, values are PlayerAccount instances.
        self._accounts = {}

        self.db_manager = DBManager(self, db_name=db_name)

    def prep_and_load(self):
        """
        Sets the :attr:`_db` reference. Does some basic DB population if
        need be.
        """

        self.db_manager.prepare_and_load()

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

        saved_account = yield self.db_manager.save_account(account)
        self._accounts[saved_account.username] = saved_account
        returnValue(saved_account)

    @inlineCallbacks
    def destroy_account(self, account):
        """
        Destroys an account by yanking it from :py:attr:`_accounts` and the DB.
        """

        yield self.db_manager.destroy_account(account)

        # Clear the object out of the store, mark it for GC.
        del self._accounts[account.username]
        del account

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
            raise AccountNotFoundException(
                'No such account with username "%s" found' % username)
