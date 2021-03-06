"""
Contains base level parents that aren't to be used directly.
"""

from twisted.internet.defer import inlineCallbacks, returnValue
from fuzzywuzzy.process import QRatio
from fuzzywuzzy import utils as fuzz_utils

from src.daemons.server.ansi import ANSI_HILITE, ANSI_NORMAL
from src.daemons.server.objects.exceptions import ObjectHasZoneMembers, NoSuchObject
from src.daemons.server.protocols.proxyamp import EmitToObjectCmd


#noinspection PyShadowingBuiltins
class BaseObject(object):
    """
    This is the base parent for every in-game "object". Rooms, Players, and
    Things are all considered objects. Behaviors here are very low level.
    """

    # Holds this object's command table. Any objects inside of this object
    # will check this for command matches before the global table.
    local_command_table = None
    # Same as above, but for admin-only commands.
    local_admin_command_table = None

    def __init__(self, mud_service, id, parent, name, description=None,
                 internal_description=None,
                 location_id=None, destination_id=None, zone_id=None,
                 aliases=None, originally_controlled_by_account_id=None,
                 controlled_by_account_id=None, attributes=None,
                 created_time=None):
        """
        :param MudService mud_service: The MudService class running the game.
        :param int id: A unique ID for the object, or None if this is
            a new object.
        :param str parent: The Python path to the parent class for this
            instantiated object.
        :param str name: The non-ASCII'd name.
        :param str description: The object's description.
        :keyword int location_id: The ID of the object this object resides within.
            None if this object is location-less.
        :keyword int destination_id: Used to determine where an exit leads.
        :keyword int zone_id: Optional zone ID (ID of another BaseObject).
        :keyword int originally_controlled_by_account_id: Account ID that
            first controlled this object (if it was created in conjunction
            with an account).
        :keyword in controlled_by_account_id: If this object is being controlled
            by an account, this will be populated.
        :keyword dict kwargs: All objects are instantiated with the values from
            the DB as kwargs. Since the DB representation of all of an
            objects attributes is just a dict, this works really well.
        :keyword datetime.datetime created_time: The time the object was
            created.
        """

        self.mud_service = mud_service

        # This mirrors the 'id' field in dott_objects. If this is set to None
        # and the instance is saved, an insert is done.
        self.id = id
        self.name = name
        self.description = description
        self.internal_description = internal_description
        self.parent = parent
        self.location_id = location_id
        self.destination_id = destination_id
        self.zone_id = zone_id
        self.aliases = aliases or []
        self.originally_controlled_by_account_id = originally_controlled_by_account_id
        self.controlled_by_account_id = controlled_by_account_id
        # This stores all of the object's data. This includes core and
        # userspace attributes.
        self._attributes = attributes or {}
        self.created_time = created_time

        assert isinstance(self._attributes, dict)

    def __str__(self):
        return "<%s: %s (#%d)>" % (self.__class__.__name__, self.name, self.id)

    def __repr__(self):
        return self.__str__()

    #
    ## Begin properties.
    #

    @property
    def _object_store(self):
        """
        Short-cut to the global object store.

        :rtype: ObjectStore
        :returns: Reference to the global object store instance.
        """

        return self.mud_service.object_store

    @property
    def _command_handler(self):
        """
        Short-cut to the global command handler.

        :rtype: CommandHandler
        :returns: Reference to the global command handler instance.
        """

        return self.mud_service.command_handler

    def _generic_id_to_baseobject_property_getter(self, attrib_name):
        """
        A generic getter for attributes that store object IDs. Given an
        object ID, retrieve it or None.

        :rtype: BaseObject or None
        :returns: The ``BaseObject`` instance for the attribute, or None
            if there is no value.
        :raises: NoSuchObject if the stored object ID has no match in
            the DB.
        """

        obj_id = getattr(self, attrib_name)
        if obj_id:
            #noinspection PyTypeChecker
            return self._object_store.get_object(obj_id)
        else:
            return None

    def _generic_baseobject_to_id_property_setter(self, attrib_name, obj_or_id):
        """
        Sets this object's zone.

        :param obj_or_id: The object or object ID to set as the
            object's zone master.
        :type obj_or_id: A ``BaseObject`` sub-class or an ``int``.
        """

        if isinstance(obj_or_id, int):
            # Already an int, assume this is an object ID.
            setattr(self, attrib_name, obj_or_id)
        elif isinstance(obj_or_id, basestring):
            raise Exception("BaseObject.set_%s() can't accept strings for object IDs: %s" % (
                attrib_name, obj_or_id))
        elif obj_or_id is None:
            setattr(self, attrib_name, None)
        else:
            # Looks like a BaseObject sub-class. Grab the object ID.
            setattr(self, attrib_name, obj_or_id.id)

    @property
    def attributes(self):
        """
        Redirects to the object's attributes dict.

        :rtype: dict
        """

        return self._attributes

    def get_location(self):
        """
        Determines the object's location and returns the instance representing
        this object's location.

        :returns: The ``BaseObject`` instance (sub-class) that this object
            is currently in. Typically a ``RoomObject``, but can also be
            other types.
        :raises: NoSuchObject if the stored object ID has no match in
            the DB.
        """

        return self._generic_id_to_baseobject_property_getter('location_id')

    def set_location(self, obj_or_id):
        """
        Sets this object's location.

        :param obj_or_id: The object or object ID to set as the
            object's location.
        :type obj_or_id: A ``BaseObject`` sub-class or a ``str``.
        """

        if self.base_type == 'room':
            # Rooms can't have locations.
            return
        self._generic_baseobject_to_id_property_setter('location_id', obj_or_id)

    location = property(get_location, set_location)

    def get_zone(self):
        """
        Determines the object's zone and returns the instance representing
        this object's zone.

        :rtype: BaseObject or None
        :returns: The ``BaseObject`` instance (sub-class) that is this object's
            zone master object.
        :raises: NoSuchObject if the stored object ID has no match in
            the DB.
        """

        return self._generic_id_to_baseobject_property_getter('zone_id')

    def set_zone(self, obj_or_id):
        """
        Sets this object's zone.

        :param obj_or_id: The object or object ID to set as the
            object's zone master.
        :type obj_or_id: A ``BaseObject`` sub-class or an ``int``.
        """

        self._generic_baseobject_to_id_property_setter('zone_id', obj_or_id)

    zone = property(get_zone, set_zone)

    #noinspection PyPropertyDefinition
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

        This should only be used for display, never for inheritance checking!
        isinstance and friends are there for that.

        :rtype: str
        """

        raise NotImplementedError('Over-ride in sub-class.')

    #
    ## Begin regular methods.
    #

    @inlineCallbacks
    def save(self):
        """
        Shortcut for saving an object to the object store it's a member of.
        """

        saved_obj = yield self._object_store.save_object(self)
        returnValue(saved_obj)

    @inlineCallbacks
    def destroy(self):
        """
        Destroys the object.
        """

        # Destroy all exits that were linked to this object.
        if self.base_type not in ['exit', 'player']:
            for exit in self._object_store.find_exits_linked_to_obj(self):
                yield exit.destroy()

        # Un-set the zones on all objects who are members of this object.
        zone_members = self._object_store.find_objects_in_zone(self)
        if zone_members:
            raise ObjectHasZoneMembers(
                "Object has zone members. @zmo/empty first, or use "
                "@zmo/delete instead.")

        # Destroys this object, once all cleanup is done.
        yield self._object_store.destroy_object(self)

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

        assert self.id is not None, "Attempting to emit to an object with no ID."

        self.mud_service.proxyamp.callRemote(
            EmitToObjectCmd,
            object_id=self.id,
            message=message
        )

    def emit_to_contents(self, message, exclude=None):
        """
        Emits the given message to everything in this object's inventory.

        :param str message: The message to emit to any object within
            this one.
        :param BaseObject exclude: A list of objects who are to be
            excluded from the emit list. These objects will not see the emit.
        """

        if not exclude:
            exclude = []
        else:
            exclude = [obj.id for obj in exclude]

        contents = self.get_contents()
        for obj in contents:
            if obj.id not in exclude:
                obj.emit_to(message)

    def move_to(self, destination_obj, force_look=True):
        """
        Moves this object to the given destination.

        :param BaseObject destination_obj: Where to move this object to.
        :param bool force_look: If True, the object will run the "look"
            command between movements.
        """

        old_location_obj = self.location

        #noinspection PyUnresolvedReferences
        old_location_obj.before_object_leaves_event(self)
        destination_obj.before_object_enters_event(self)

        self.set_location(destination_obj)
        self.save()

        #noinspection PyUnresolvedReferences
        old_location_obj.after_object_leaves_event(self)
        destination_obj.after_object_enters_event(self)

        if force_look:
            self.execute_command('look')

    def is_admin(self):
        """
        This always returns ``False``, since objects don't have administrative
        powers by default.

        :rtype: bool
        :returns: ``False``
        """

        return False

    def get_contents(self):
        """
        Returns the list of objects 'inside' this object.

        :rtype: list
        :returns: A list of :class:`BaseObject` instances whose location is
            this object.
        """

        return self._object_store.get_object_contents(self)

    #noinspection PyUnusedLocal
    def get_description(self, invoker, from_inside=False):
        """
        Returns the description of this object.

        :param BaseObject invoker: The object asking for the description.
        :param bool from_inside: If True, use an internal description instead
            of the normal description, if available. For example, the inside
            of a vehicle should have a different description than the outside.
        """

        if from_inside and self.internal_description:
            return self.internal_description

        return self.description

    def get_appearance_name(self, invoker, force_admin_view=False):
        """
        Returns the 'pretty' form of the name for the object's appearance.

        :param invoker: The object asking for the appearance. If None is
            provided, provide the non-admin view.
        :type invoker: BaseObject or None
        :param bool force_admin_view: If this is True, force the adin view,
            even if the invoker is not an admin (or no invoker is given).
        :rtype: str
        :returns: The object's 'pretty' name.
        """

        if (invoker and invoker.is_admin()) or force_admin_view:
            # Used to show a single-character type identifier next to object id.
            if self.base_type == 'room':
                type_str = 'R'
            elif self.base_type == 'thing':
                type_str = 'T'
            elif self.base_type == 'exit':
                type_str = 'E'
            elif self.base_type == 'player':
                type_str = 'P'
            else:
                # Wtf dis?
                type_str = 'U'

            extra_info = '(#%s%s)' % (
                self.id,
                type_str,
            )
        else:
            extra_info = ''

        return "%s%s%s%s" % (ANSI_HILITE, self.name, ANSI_NORMAL, extra_info)

    #noinspection PyUnusedLocal
    def get_appearance_contents_and_exits(self, invoker, from_inside=False):
        """
        Returns the contents and exits display for the object.

        :param BaseObject invoker: The object asking for the appearance.
        :param bool from_inside: Show the contents/exits as if the invoker
            was inside this object.
        :rtype: str
        :returns: The contents/exits display.
        """

        exits_str = ''
        things_str = ''

        contents = self.get_contents()
        for obj in contents:
            if obj.id == invoker.id:
                # This is the invoker, don't show yourself.
                continue

            if obj.base_type == 'exit':
                # Exits show the exit's primary alias.
                obj_alias = obj.aliases[0] if obj.aliases else '_'
                exits_str += '<%s> %s\n' % (
                    obj_alias,
                    obj.get_appearance_name(invoker),
                )
            else:
                # Everything else just shows the name.
                things_str += '%s\n' % obj.get_appearance_name(invoker)

        retval = ''

        if things_str:
            retval += '\nContents:\n'
            retval += things_str

        if exits_str:
            retval += '\nExits:\n'
            retval += exits_str

        return retval

    def get_appearance(self, invoker):
        """
        Shows the full appearance for an object. Includes description, contents,
        exits, and everything else.

        :param BaseObject invoker: The object asking for the appearance.
        :rtype: str
        :returns: The object's appearance, from the outside or inside.
        """

        #noinspection PyUnresolvedReferences
        is_inside = invoker.location.id == self.id

        desc = self.get_description(invoker, from_inside=is_inside)
        name = self.get_appearance_name(invoker)
        contents = self.get_appearance_contents_and_exits(
            invoker,
            from_inside=is_inside
        )

        return "%s\n%s\n%s" % (name, desc, contents)

    def _find_name_or_alias_match(self, objects, query):
        """
        Performs name and alias matches on a list of objects. Returns the
        best match, or ``None`` if nothing was found.

        :param iterable objects: A list of ``BaseObject`` sub-class instances
            to attempt to match to.
        :param str query: The string to match against.
        :rtype: BaseObject
        :returns: The best match object for the given query.
        """

        if not objects:
            return None

        for obj in objects:
            # Start by checking all objects for an alias match.
            aliases = [alias.lower() for alias in obj.aliases]
            if query.lower() in aliases:
                # If a match is found, return immediately on said match.
                return obj

        processor = lambda x: fuzz_utils.full_process(x)

        for choice in objects:
            processed = processor(choice.name)
            if query in processed:
                return choice

        return None

    def _find_object_id_match(self, desc):
        """
        Given an object ID string (ie: '#9'), determine whether this object
        can find said object.

        :param str desc: A string with which to perform a search
        :rtype: :class:'BaseObject' or ``None``
        :returns: An object that best matches the string provided. If no
            suitable match was found, returns ``None``.
        """

        mud_service = self.mud_service

        try:
            # Object IDs are int primary keys in the object store.
            obj_id = int(desc[1:])
        except (ValueError, TypeError):
            # This isn't an object ID.
            return None

        # Absolute object identifier: lookup the id
        try:
            obj = mud_service.object_store.get_object(obj_id)
        except NoSuchObject:
            return None

        if not self.is_admin():
            # Non-admins can only find objects in their current location.
            if self.location and obj.location:
                # Both invoker and the target have a location. See if they
                # are in the same place.
                #noinspection PyUnresolvedReferences
                location_match = self.location.id == obj.location.id or \
                    self.location.id == obj.id
                if location_match:
                    # Locations match. Good to go.
                    return obj
            elif obj.base_type == 'room':
                #noinspection PyUnresolvedReferences
                if self.location and self.location.id == obj.id:
                    # Non-admin is looking at their current location, which
                    # is a room.
                    return obj
            else:
                # Non-specified or differing locations. Either way, there
                # is no usable match.
                return None
        else:
            # Invoker is an admin, and can find object id matches globally.
            return obj

    def contextual_object_search(self, desc):
        """
        Searches for objects using the current object as a frame of
        reference

        :param str desc: A string with which to perform a search
        :rtype: :class:'BaseObject' or ``None``
        :returns: An object that best matches the string provided. If no
            suitable match was found, returns ``None``.
        """

        desc = desc.strip()
        if not desc:
            # Probably an empty string, which we can't do much with.
            return None

        if desc[0] == '#':
            oid_match = self._find_object_id_match(desc)
            if oid_match:
                return oid_match

        if desc.lower() == 'me':
            # Object is referring to itself
            return self

        if desc.lower() == 'here':
            # Object is referring to it's location
            return self.location

        # Not a keyword, begin fuzzy search

        # First search the objects in the room
        if self.location:
            #noinspection PyUnresolvedReferences
            neighboring_match = self._find_name_or_alias_match(
                self.location.get_contents(),
                desc
            )
            if neighboring_match:
                return neighboring_match

        # Next search the objects inside the invoker
        inventory_match = self._find_name_or_alias_match(
            self.get_contents(),
            desc
        )
        if inventory_match:
            return inventory_match

        # Unable to find anything
        return None

    def can_object_enter(self, obj):
        """
        Determine whether another object can enter this object.

        :param BaseObject obj: The object to check enter permissions for.
        :rtype: tuple
        :returns: A tuple in the format of ``(can_enter, message)``, where
            ``can_enter`` is a bool, and ``message`` is a string or ``None``,
            used to provide a reason for the object not being able to enter.
        """

        if obj.is_admin():
            # Admin can enter anything.
            return True, None

        return False, "You can't enter that."

    def determine_enter_destination(self, obj):
        """
        Given an object that is going to enter this one, determine where said
        object will be moved to. This defaults to this object's inventory,
        but in the case of something like a ship, they should enter to the
        bridge.

        :param BaseObject obj: The other object that is entering this one.
        :rtype: BaseObject
        :returns: The target location for the object to be moved to upon
            entering this object.
        """

        return self

    def can_object_leave(self, obj):
        """
        Determine whether another object can leave this object.

        :param BaseObject obj: The object to check enter permissions for.
        :rtype: tuple
        :returns: A tuple in the format of ``(can_leave, message)``, where
            ``can_leave`` is a bool, and ``message`` is a string or ``None``,
            used to provide a reason for the object not being able to leave.
        """

        if not obj.location:
            return False, "You can't find a way out."

        # All is well
        return True, None

    def determine_leave_destination(self, obj):
        """
        Given an object that is going to leave this one, determine where said
        object will be moved to. This defaults to this object's location,
        but in the case of leaving a ship's bridge, they should end up outside
        the ship, rather than inside the ship object.

        :param BaseObject obj: The other object that is entering this one.
        :rtype: BaseObject
        :returns: The target location for the object to be moved to upon
            leaving this object.
        """

        return self.location

    #
    ## Begin events
    #

    def after_session_connect_event(self):
        """
        This is called when the proxy authenticates and logs in a Session that
        controls this object. This event is only triggered when the first
        Session controlling this object is logged in. For example, logging in
        a second time with another client would not trigger this again.

        This is currently only meaningful for PlayerObject instances. We don't
        want players to see connects/disconnects when admins are controlling
        NPCs.
        """

        pass

    def after_session_disconnect_event(self):
        """
        This is called when the last Sesssion that controls this object is
        disconnected. If you have two clients open that are authenticated and
        controlling the same object, this will not trigger until the last
        Session is closed.

        This is currently only meaningful for PlayerObject instances. We don't
        want players to see connects/disconnects when admins are controlling
        NPCs.
        """

        pass

    #noinspection PyUnusedLocal
    def before_object_leaves_event(self, actor):
        """
        Triggered before an object leaves this object's inventory.

        :param BaseObject actor: The object doing the leaving.
        """

        pass

    #noinspection PyUnusedLocal
    def after_object_leaves_event(self, actor):
        """
        Triggered after an object physically leaves this object's inventory.

        :param BaseObject actor: The object doing the leaving.
        """

        for obj in self.get_contents():
            # Can't use self.emit_to_contents because we need to determine
            # appearance on a per-object basis.
            obj.emit_to('%s has left' % actor.get_appearance_name(obj))

    #noinspection PyUnusedLocal
    def before_object_enters_event(self, actor):
        """
        Triggered before an object arrives in this object's inventory.

        :param BaseObject actor: The object doing the entering.
        """

        for obj in self.get_contents():
            # Can't use self.emit_to_contents because we need to determine
            # appearance on a per-object basis.
            obj.emit_to('%s has arrived' % actor.get_appearance_name(obj))

    #noinspection PyUnusedLocal
    def after_object_enters_event(self, actor):
        """
        Triggered after an object physically enters this object's inventory.

        :param BaseObject actor: The object doing the entering.
        """

        pass