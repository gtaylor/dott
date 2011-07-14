class BaseObject(object):
    """
    This is the base parent for every in-game "object". Rooms, Players, and
    Things are all considered objects. Behaviors here are very low level.
    """
    def __init__(self, object_store, **kwargs):
        """
        :param InMemoryObjectStore object_store: Reference to the global
            object store that is holding this object.
        :keyword dict kwargs: All objects are instantiated with the values from
            the DB as kwargs. Since the DB representation of all of an
            objects attributes is just a dict, this works really well.
        """
        self._object_store = object_store
        self._account_store = object_store._account_store

        # This stores all of the object's data. This includes core and
        # userspace attributes.
        self.odata = kwargs

        # The 'attributes' key in the odata dict contains userspace attributes,
        # which are "user" defined (user being the developer), rather than
        # the core attributes in the top level of the dict.
        if not self.odata.has_key('attributes'):
            # No attributes dict found, create one so it may be saved to the DB.
            self.odata['attributes'] = {}

    def __getattr__(self, name):
        """
        If the user requests an attribute that can't be found on an object,
        assume they're looking for a core attribute. They can also get at the
        userspace attributes.

        :param str name: The attribute the user is looking for.
        :returns: The requested value, pulled from :attrib:`odata`.
        :raises: AttributeError if no match is found in :attrib:`odata`.
        """
        if self.odata.has_key(name):
            return self.odata[name]

        raise AttributeError()

    def save(self):
        """
        Shortcut for saving an object to the object store it's a member of.
        """
        self._object_store.save_object(self)

    def get_id(self):
        """
        Returns the object's ID. This is a CouchDB hash string.

        :rtype: str
        :returns: The object's ID.
        """
        return self.odata['_id']
    def set_id(self, id):
        """
        Be really careful doing this. Sets the room's ID, but no duplication
        checks are performed.

        :param str id: The new ID to set.
        """
        self.odata['_id'] = id
    id = property(get_id, set_id)

    def get_account_controlled_by(self):
        """
        Returns the PlayerAccount that is controlling this object, or ``None``
        if the object is un-controlled.

        .. note:: Controlled does not mean connected.

        :rtype: :class:`src.server.accounts.account.PlayerAccount` or ``None``
        :returns: If controlled by an account, returns the account. If nothing
            controls this object, returns ``None``.
        """
        return self._account_store.get_account(self.controlled_by_account)

    def get_location(self):
        """
        Determines the object's location and returns the instance representing
        this object's location.

        :returns: The ``BaseObject`` instance (sub-class) that this object
            is currently in. Typically a ``RoomObject``, but can also be
            other types.
        """
        loc_id = self.odata.get('location_id')
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
            self.odata['location_id'] = obj_or_id
        else:
            self.odata['location_id'] = obj_or_id._id
    location = property(get_location, set_location)