from src.server.protocols.proxyamp import EmitToObjectCmd
from fuzzywuzzy import fuzz

class BaseObject(object):
    """
    This is the base parent for every in-game "object". Rooms, Players, and
    Things are all considered objects. Behaviors here are very low level.
    """
    def __init__(self, mud_service, **kwargs):
        """
        :param MudService mud_service: The MudService class running the game.
        :keyword dict kwargs: All objects are instantiated with the values from
            the DB as kwargs. Since the DB representation of all of an
            objects attributes is just a dict, this works really well.
        """
        self._mud_service = mud_service

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

    @property
    def _object_store(self):
        """
        Short-cut to the global object store.

        :rtype: InMemoryObjectStore
        :returns: Reference to the global object store instance.
        """
        return self._mud_service.object_store

    @property
    def _command_handler(self):
        """
        Short-cut to the global command handler.

        :rtype: CommandHandler
        :returns: Reference to the global command handler instance.
        """
        return self._mud_service.command_handler

    @property
    def attributes(self):
        """
        Returns a reference to the attributes dict within self._odata.
        These are anything but the bare minimum things like object ID,
        location, parent, name, etc.

        :rtype: dict
        :returns: A dict of additional attributes for the object.
        """
        return self._odata['attributes']

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
            self._odata['location_id'] = obj_or_id.id
    location = property(get_location, set_location)

    def get_controlled_by_id(self):
        """
        Returns the ID of the PlayerAccount that is controlling this object,
        or ``None`` if the object is un-controlled.

        .. note:: Controlled does not mean connected.

        :rtype: str
        :returns: The CouchDB ID of the PlayerAccount that controls this object.
        """
        return self._odata.get('controlled_by_account_id')
    
    def set_controlled_by_id(self, account_id):
        """
        Sets the PlayerAccount ID that controls this object.

        :param str account_id: The CouchDB ID of the PlayerAccount that
            controls this object.
        """
        self._odata['controlled_by_account_id'] = account_id
    controlled_by_id = property(get_controlled_by_id, set_controlled_by_id)

    @property
    def base_type(self):
        """
        BaseObject's primary three sub-classes are Room, Player, Exit,
        and Thing. These are all considered the top-level children, and
        everything else will be children of them. Room, Player, Exit, and
        Thing are the only three valid base types, and each parent should
        return one of the following for quick-and-easy type checking:

            * room
            * player
            * exit
            * thing

        :rtype: str
        """
        raise NotImplementedError('Over-ride in sub-class.')

    #
    ## Begin regular methods.
    #

    def save(self):
        """
        Shortcut for saving an object to the object store it's a member of.
        """
        self._object_store.save_object(self)

    def execute_command(self, command_string):
        """
        Directs the object to execute a certain command. Passes the command
        string through the command handler.

        :param str command_string: The command to run.
        """
        # Input gets handed off to the command handler, where it is parsed
        # and routed through various command tables.
        if not self._command_handler.handle_input(self, command_string):
            self.emit_to('Huh?')

    def emit_to(self, message):
        """
        Emits to any Session objects attached to this object.

        :param str message: The message to emit to any Sessions attached to
            the object.
        """
        self._mud_service.proxyamp.callRemote(
            EmitToObjectCmd,
            object_id=self.id,
            message=message
        )

    def get_contents(self):
        """
        Returns the list of objects 'inside' this object.

        :rtype: list
        :returns: A list of :class:`BaseObject` instances whose location is
            this object.
        """
        return self._object_store.get_object_contents(self)

    def get_description(self, from_inside=False):
        """
        Returns the description of this object. Typically just hits the
        'description' odata attribute.

        :keyword bool from_inside: If True, use an internal description instead
            of the normal description, if available. For example, the inside
            of a vehicle should have a different description than the outside.
        """
        if from_inside:
            idesc = self.attributes.get('internal_description')
            if idesc:
                return idesc

        description = self.attributes.get(
            'description',
            'You see nothing special.'
        )
        return description

    def get_appearance(self, invoker):
        """
        Shows the full appearance for an object. Includes description, contents,
        exits, and everything else.

        :param BaseObject invoker: The object asking for the appearance.
        """
        is_inside = invoker.location.id == self.id

        ansi_hilight = "\033[1m"
        ansi_normal = "\033[0m"
        name = "%s%s%s" % (ansi_hilight, self.name, ansi_normal)

        desc = self.get_description(from_inside=is_inside)

        return "%s\n%s" % (name, desc)

    def contextual_object_search(self, desc):
        """
        Searches for objects using the current object as a frame of
        reference

        :param str desc: A string with which to perform a search

        :rtype: :class:'BaseObject'
        :returns: An object that best matches the string provided
        """

        desc = desc.strip()
        mud_service = self._mud_service

        if desc[0] == '#':
            # Absolute dbref identifier: lookup the id
            return mud_service.object_store.get_object(desc[1:])

        if desc.lower() == 'me':
            # Object is referring to itself
            return self

        if desc.lower() == 'here':
            # Object is referring to it's location
            return self.location

        # Not a keyword, begin fuzzy search

        # First search the objects in the room
        location = self.location
        if location:
            ratio = 0
            result = None
            for obj in location.get_contents():
                r = fuzz.partial_ratio(desc, obj.name)
                if r > 50 and r > ratio:
                    ratio = r
                    result = obj
            if result:
                return result

        # Next search the objects inside the invoker
        ratio = 0
        result = None
        for obj in self.get_contents():
            r = fuzz.partial_ratio(desc, obj.name)
            if r > 50 and r > ratio:
                ratio = r
                result = obj
        if result:
            return result

        # Unable to find anything
        return None


    #
    ## Begin events
    #

    def at_player_connect_event(self):
        """
        This is called when a PlayerAccount logs in. Whatever object it is
        controlling has this method called on it.
        """
        # Only PlayerObject does anything with this right now.
        pass

    def at_player_disconnect_event(self):
        """
        This is called when a PlayerAccount disconnects. Whatever object it is
        controlling has this method called on it.
        """
        # Only PlayerObject does anything with this right now.
        pass