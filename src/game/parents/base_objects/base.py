class BaseObject(object):
    """
    This is the base parent for every in-game "object". Rooms, Players, and
    Things are all considered objects. Behaviors here are very low level.
    """
    def __init__(self, object_store, command_handler, **kwargs):
        """
        :param InMemoryObjectStore object_store: Reference to the global
            object store that is holding this object.
        :param CommandHandler command_handler: Reference to the global
            command handler.
        :keyword dict kwargs: All objects are instantiated with the values from
            the DB as kwargs. Since the DB representation of all of an
            objects attributes is just a dict, this works really well.
        """
        self._object_store = object_store
        self._command_handler = command_handler
        self._account_store = object_store._account_store

        # This stores all of the object's data. This includes core and
        # userspace attributes.
        self._odata = kwargs

        # The 'attributes' key in the _odata dict contains userspace attributes,
        # which are "user" defined (user being the developer), rather than
        # the core attributes in the top level of the dict.
        if not self._odata.has_key('attributes'):
            # No attributes dict found, create one so it may be saved to the DB.
            self._odata['attributes'] = {}

    #
    ## Begin properties.
    #

    def get_id(self):
        """
        Returns the object's ID. This is a CouchDB hash string.

        :rtype: str
        :returns: The object's ID.
        """
        return self._odata['_id']
    def set_id(self, new_id):
        """
        Be really careful doing this. Sets the room's ID, but no duplication
        checks are performed.

        :param str new_id: The new ID to set.
        """
        self._odata['_id'] = new_id
    id = property(get_id, set_id)

    def get_name(self):
        """
        Returns the object's name.

        :rtype: str
        :returns: The object's name.
        """
        return self._odata['name']
    def set_name(self, name):
        """
        Sets the object's name.

        :param str name: The new name for the object.
        """
        self._odata['name'] = name
    name = property(get_name, set_name)

    def get_parent(self):
        """
        Returns the object's parent class.

        :rtype: str
        :returns: The object's parent class.
        """
        return self._odata['parent']
    def set_parent(self, parent_class_path):
        """
        Sets the object's parent.

        :param str parent_class_path: The new name for the object.
        """
        self._odata['parent'] = parent_class_path
    parent = property(get_parent, set_parent)

    def get_location(self):
        """
        Determines the object's location and returns the instance representing
        this object's location.

        :returns: The ``BaseObject`` instance (sub-class) that this object
            is currently in. Typically a ``RoomObject``, but can also be
            other types.
        """
        loc_id = self._odata.get('location_id')
        if loc_id:
            return self._object_store.get_object(loc_id)
        else:
            return None
    def set_location(self, obj_or_id):
        """
        Sets this object's location.

        :param obj_or_id: The object or object ID to set as the
            object's location.
        :type obj_or_id: A ``BaseObject`` sub-class or a ``str``.
        """
        if isinstance(obj_or_id, basestring):
            self._odata['location_id'] = obj_or_id
        else:
            self._odata['location_id'] = obj_or_id._id
    location = property(get_location, set_location)

    def get_controlled_by(self):
        """
        Returns the PlayerAccount that is controlling this object, or ``None``
        if the object is un-controlled.

        .. note:: Controlled does not mean connected.

        :rtype: :class:`src.server.accounts.account.PlayerAccount` or ``None``
        :returns: If controlled by an account, returns the account. If nothing
            controls this object, returns ``None``.
        """
        username = self._odata.get('controlled_by_account_id')
        if username:
            return self._account_store.get_account(username)
        else:
            return None
    def set_controlled_by(self, account_or_username):
        """
        Sets the PlayerAccount that controls this object.

        :param account_or_username: The account or username that controls
            this object.
        :type account_or_username: A
            :class:`src.accounts.account.PlayerAccount` or ``str``.
        """
        if isinstance(account_or_username, basestring):
            self._odata['controlled_by_account_id'] = account_or_username
        else:
            self._odata['controlled_by_account_id'] = account_or_username.username
    controlled_by = property(get_controlled_by, set_controlled_by)

    #
    ## Begin regular methods.
    #

    def save(self):
        """
        Shortcut for saving an object to the object store it's a member of.
        """
        self._object_store.save_object(self)
