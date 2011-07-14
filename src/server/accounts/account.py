import hashlib

import settings

class PlayerAccount(object):
    """
    This class abstracts accounts out, and is specific to the
    InMemoryAccountStore backend.
    """
    def __init__(self, account_store, object_store,
                 **kwargs):
        """
        :param InMemoryAccountStore account_store: The account store that
            instantiated this object.
        :param InMemoryObjectStore the global object store.

        :keyword str _id: The username for the account.
        :keyword str email: The email address associated with this account.
        :keyword str password: The encrypted password string.
        :keyword str currently_controlling_id: The ID of the Object this
            account is currently controlling.
        """
        self._account_store = account_store
        self._object_store = object_store

        self._odata = kwargs

    #
    ## Begin properties
    #

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

    def get_currently_controlling(self):
        """
        Determines what object this account is currently controlling and
        returns it.

        :returns: An instance of a :class:`BaseObject` sub-class, or
            ``None`` if this account is not controlling anything.
        """
        controlled_id = self._odata.get('currently_controlling_id')
        if controlled_id:
            return self._object_store.get_object(controlled_id)
        return None
    def set_currently_controlling(self, obj_or_id):
        """
        Sets what this account is controlling.

        :param obj_or_id: The object or object ID to set as the thing
            being controlled by this account.
        :type obj_or_id: A ``BaseObject`` sub-class or a ``str``.
        """
        if isinstance(obj_or_id, basestring):
            self._odata['currently_controlling_id'] = id
        else:
            self._odata['currently_controlling_id'] = obj_or_id._id
    currently_controlling = property(get_currently_controlling,
                                     set_currently_controlling)

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