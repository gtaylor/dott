import hashlib

import settings


class PlayerAccount(object):
    """
    This class abstracts accounts out, and is specific to the
    InMemoryAccountStore backend.
    """

    def __init__(self, mud_service, **kwargs):
        """
        :param MudService server: The top-level MudService instance found in
            dott.tac.

        :keyword str _id: The username for the account.
        :keyword str email: The email address associated with this account.
        :keyword str password: The encrypted password string.
        :keyword str currently_controlling_id: The ID of the Object this
            account is currently controlling.
        """

        self._mud_service = mud_service

        self._odata = kwargs

    #
    ## Begin properties
    #

    @property
    def _account_store(self):
        """
        Short-cut to the global account store.

        :rtype: InMemoryAccountStore
        :returns: Reference to the global account store instance.
        """

        return self._mud_service.account_store

    def get_username(self):
        """
        The account's username serves as its CouchDB _id.

        :rtype: str
        :returns: The account's username.
        """

        return self._odata['_id']

    def set_username(self, username):
        """
        Sets the account's username to something else.

        .. warning:: Be careful with this, we might need to detect for
            collisions manually, or risk over-writing accounts.
        """

        self._odata['_id'] = username
    username = property(get_username, set_username)

    def get_currently_controlling_id(self):
        """
        Determines what object this account is currently controlling and
        returns it.

        :returns: An instance of a :class:`BaseObject` sub-class, or
            ``None`` if this account is not controlling anything.
        """

        return self._odata.get('currently_controlling_id')

    def set_currently_controlling_id(self, obj_id):
        """
        Sets what this account is controlling.

        :param obj_id: The object ID to set as the thing
            being controlled by this account.
        :type obj_id: ``str``
        """

        self._odata['currently_controlling_id'] = obj_id
    currently_controlling_id = property(get_currently_controlling_id,
                                        set_currently_controlling_id)

    #
    ## Begin regular methods.
    #

    def save(self):
        """
        Shortcut for saving an object to the account store.
        """

        self._account_store.save_account(self)

    @property
    def password(self):
        """
        Returns the raw, SHA512'd password hash.

        :rtype: str
        :returns: The SHA512 password hash.
        """

        return self._odata['password']

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

        self._odata['password'] = self._get_hash_for_password(new_password)

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