import hashlib
from twisted.internet.defer import inlineCallbacks

import settings


class PlayerAccount(object):
    """
    This class abstracts accounts out, and is specific to the
    AccountStore backend.
    """

    def __init__(self, proxy_service, id, username, currently_controlling_id,
                 email, password=None):
        """
        :param ProxyService proxy_service: The top-level proxy service
            instance found in dott.tac.

        :keyword int id: A unique ID for the object, or None if this is
            a new account.
        """

        self._proxy_service = proxy_service

        self.id = id
        self.username = username
        self.currently_controlling_id = currently_controlling_id
        self.email = email
        self.password = password

    #
    ## Begin properties
    #

    @property
    def _account_store(self):
        """
        Short-cut to the global account store.

        :rtype: AccountStore
        :returns: Reference to the global account store instance.
        """

        return self._proxy_service.account_store

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