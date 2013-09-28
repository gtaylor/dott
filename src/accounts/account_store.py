# -*- test-case-name: src.accounts.tests -*-
"""
Lower level account management.
"""

from twisted.internet.defer import inlineCallbacks, returnValue

from src.accounts.db_io import DBManager
from src.accounts.exceptions import AccountNotFoundException, UsernameTakenException
from src.accounts.account import PlayerAccount


class AccountStore(object):
    """
    Serves as an in-memory store for all account values.
    """

    def __init__(self, db_name=None):
        """
        :keyword str db_name: Overrides the DB name for the account DB.
        """

        # All DB operations happen through here.
        self.db_manager = DBManager(self, db_name=db_name)

    @inlineCallbacks
    def prep_and_load(self):
        """
        Creates DB connection objects. Makes sure the account-related
        tables exists. Creates it if it doesn't.
        """

        yield self.db_manager.prepare_and_load()

    @inlineCallbacks
    def create_account(self, username, password, email):
        """
        Creates and returns a new account. Makes sure the username is unique.

        :param str username: The username of the account to create.
        :param str password: The raw (un-encrypted) password.
        :param str email: The player's email address.
        :rtype: :class:`PlayerAccount`
        :returns: The newly created account.
        :raises: :class:`UsernameTakenException` if someone attempts to create
            a duplicate account.
        """

        try:
            yield self.get_account_by_username(username)
            raise UsernameTakenException(
                "User with that username already exists.")
        except AccountNotFoundException:
            pass

        # Create the PlayerAccount, pointed at the PlayerObject's _id.
        #noinspection PyTypeChecker
        account = PlayerAccount(
            self,
            # This will be set after the first save.
            id=None,
            username=username,
            email=email,
            # This will be populated on first login.
            currently_controlling_id=None,
            password=None,
        )
        # Hashes the password for safety.
        account.set_password(password)
        yield account.save()
        returnValue(account)

    @inlineCallbacks
    def save_account(self, account):
        """
        Saves an account to the DB. If the PlayerAccount's ``id`` attrib is
        ``None``, it will be populated with an int PK value when the response
        comes back from the DB.

        :param PlayerAccount account: The account to save.
        """

        saved_account = yield self.db_manager.save_account(account)
        returnValue(saved_account)

    @inlineCallbacks
    def destroy_account(self, account):
        """
        Destroys an account by dropping it from the DB.

        :param PlayerAccount account: The account to drop.
        """

        yield self.db_manager.destroy_account(account)

    @inlineCallbacks
    def get_account_count(self):
        """
        :rtype: int
        :returns: A total count of active accounts.
        """

        num_accounts = yield self.db_manager.get_account_count()
        returnValue(num_accounts)

    @inlineCallbacks
    def get_account_by_id(self, account_id):
        """
        Retrieves the requested :class:`PlayerAccount` instance.

        :param id account_id: The ID of the account to return.
        :rtype: :class:`PlayerAccount`
        :returns: The requested account.
        :raises: AccountNotFoundException if no PlayerAccount with the given
            ID exists.
        """

        account_id = int(account_id)
        account = yield self.db_manager.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundException(
                'Invalid account ID requested: %s' % account_id)
        else:
            returnValue(account)

    @inlineCallbacks
    def get_account_by_username(self, username):
        """
        Retrieves the PlayerAccount object matching the given username.

        :param str username: The username to search for. This is not
            case sensitive.
        :rtype: :class:`PlayerAccount`
        :returns: The requested account.
        :raises: AccountNotFoundException if no PlayerAccount with the given
            username exists.
        """

        lowered_username = username.lower()

        account = yield self.db_manager.get_account_by_username(lowered_username)
        if not account:
            raise AccountNotFoundException(
                'No account with username "%s" exists.' % lowered_username)
        else:
            returnValue(account)