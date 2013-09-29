import hashlib
from twisted.internet.defer import inlineCallbacks

import settings


class PlayerAccount(object):
    """
    This class abstracts accounts out, and is specific to the
    AccountStore backend.
    """

    #noinspection PyShadowingBuiltins
    def __init__(self, account_store, id, username, currently_controlling_id,
                 email, password, created_time=None):
        """
        :param AccountStore account_store: A reference to an AccountStore
            instance.
        :param id: A unique ID for the object, or None if this is
            a new account.
        :type id: int or None
        :param str username: A unique username for the Account.
        :param currently_controlling_id: The ID of the object that this
            account is currently controlling. If this is a None, a new
            PlayerObject will be created on the MUD server the first time
            this account connects.
        :type currently_controlling_id: int or None
        :param str email: The email associated with the account.
        :password str password: The account's hashed password. This is omitted
            when creating new accounts, since passwords are randomly generated.
        :param datetime.datetime created_time: The time the account was
            created.
        """

        self._account_store = account_store

        self.id = id
        self.username = username
        self.currently_controlling_id = currently_controlling_id
        self.email = email
        self.password = password
        self.created_time = created_time

    #
    ## Begin regular methods.
    #

    @inlineCallbacks
    def save(self):
        """
        Shortcut for saving an object to the account store. If this account
        instance lacked a value for :py:attr:`id`, it will have one after
        this fires.
        """

        yield self._account_store.save_account(self)

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
            through :class:`AccountStore`.

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