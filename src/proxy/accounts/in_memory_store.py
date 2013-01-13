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

    @inlineCallbacks
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

        # Create the PlayerAccount, pointed at the PlayerObject's _id.
        account = PlayerAccount(
            self._mud_service,
            # This will be set after the first save.
            id=None,
            username=username,
            email=email,
            # We'll go back and adjust this.
            currently_controlling_id=None,
            password=None,
        )
        # Hashes the password for safety.
        account.set_password(password)
        yield account.save()

        results = yield self._mud_service.proxyamp.callRemote(
            CreatePlayerObjectCmd,
            account_id=account.id,
            username=username,
        )

        account.currently_controlling_id = results['object_id']
        yield account.save()

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

    def get_account(self, account_id):
        """
        Retrieves the requested :class:`PlayerAccount` instance.

        :param id account_id: The ID of the account to return.
        :rtype: :class:`PlayerAccount`
        :returns: The requested account.
        :raises: AccountNotFoundException if no PlayerAccount with the given
            ID exists.
        """

        try:
            return self._accounts[account_id]
        except KeyError:
            raise AccountNotFoundException(
                'Invalid account ID requested: %s' % account_id)

    def get_account_by_username(self, username):
        """
        Retrieves the PlayerAccount object matching the given username.

        .. note:: This is much slower than :py:meth:`get_account`.

        :param str username: The username to search for. This is not
            case sensitive.
        :rtype: :class:`PlayerAccount`
        :returns: The requested account.
        :raises: AccountNotFoundException if no PlayerAccount with the given
            username exists.
        """

        lowered_username = username.lower()

        #TODO: Use a deferred generator?
        for id, player in self._accounts.items():
            if player.username.lower() == lowered_username:
                return player

        raise AccountNotFoundException(
            'Invalid username requested: %s' % username)