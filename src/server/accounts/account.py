import hashlib

import settings

class PlayerAccount(object):
    """
    This class abstracts accounts out, and is specific to the
    InMemoryAccountStore backend.
    """
    def __init__(self, account_store, object_store, **kwargs):
        """
        :param InMemoryAccountStore account_store: The account store that
            instantiated this object.
        :param InMemoryObjectStore the global object store.
        :param dict kwargs: All accounts are instantiated with the values from
            the DB as kwargs. Since the DB representation of all of an
            account attributes is just a dict, this works really well.
        """
        self._account_store = account_store
        self._object_store = object_store

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

    def save(self):
        """
        Shortcut for saving an object to the account store.
        """
        self._account_store.save_account(self)

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
        self.odata['password'] = self._get_hash_for_password(new_password)

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

    def get_controlled_object(self):
        """
        Determines what object this account is currently controlling and
        returns it.
        """
        return self._object_store.get_object(self.currently_controlling_id)