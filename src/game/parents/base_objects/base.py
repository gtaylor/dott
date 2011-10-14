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

    def get_aliases(self):
        """
        Returns the object's list of aliases.

        :rtype: str
        :returns: The object's list of aliases.
        """
        return self._odata.get('aliases', [])
    def set_aliases(self, aliases):
        """
        Sets the object's aliases.

        :param str aliases: The new list of aliases for the object.
        """
        if not isinstance(aliases, list):
            aliases = [aliases]
        self._odata['aliases'] = aliases
    aliases = property(get_aliases, set_aliases)

    def get_description(self):
        """
        Returns the object's description.

        :rtype: str
        :returns: The object's description.
        """
        return self._odata.get('description', 'You see nothing special')
    def set_description(self, description):
        """
        Sets the object's description.

        :param str description: The new description for the object.
        """
        self._odata['description'] = description
    description = property(get_description, set_description)

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
        if self.base_type == 'room':
            # Rooms can't have locations.
            return

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

    def save(self):
        """
        Shortcut for saving an object to the object store it's a member of.
        """
        self._object_store.save_object(self)

    def destroy(self):
        """
        Destroys the object.
        """
        self._object_store.destroy_object(self)

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

    def move_to(self, destination_obj, force_look=True):
        """
        Moves this object to the given destination.

        :param BaseObject destination_obj: Where to move this object to.
        """
        if self.location:
            #noinspection PyUnresolvedReferences
            self.location.before_object_leaves_event(self)

        destination_obj.before_object_enters_event(self)

        self.set_location(destination_obj)

        if self.location:
            #noinspection PyUnresolvedReferences
            self.location.after_object_leaves_event(self)

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

    def get_description(self, invoker, from_inside=False):
        """
        Returns the description of this object.

        :param BaseObject invoker: The object asking for the description.
        :keyword bool from_inside: If True, use an internal description instead
            of the normal description, if available. For example, the inside
            of a vehicle should have a different description than the outside.
        """
        if from_inside:
            idesc = self.attributes.get('internal_description')
            if idesc:
                return idesc

        return self.description

    def get_appearance_name(self, invoker):
        """
        Returns the 'pretty' form of the name for the object's appearance.

        :param BaseObject invoker: The object asking for the appearance.
        :rtype: str
        :returns: The object's 'pretty' name.
        """
        ansi_hilight = "\033[1m"
        ansi_normal = "\033[0m"

        if invoker.is_admin():
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

        return "%s%s%s%s" % (ansi_hilight, self.name, ansi_normal, extra_info)

    #noinspection PyUnusedLocal
    def get_appearance_contents_and_exits(self, invoker, from_inside=False):
        """
        Returns the contents and exits display for the object.

        :param BaseObject invoker: The object asking for the appearance.
        :keyword bool from_inside: Show the contents/exits as if the invoker
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
        is_inside = invoker.location.id == self.id

        desc = self.get_description(invoker, from_inside=is_inside)
        name = self.get_appearance_name(invoker)
        contents = self.get_appearance_contents_and_exits(
            invoker,
            from_inside=is_inside
        )

        return "%s\n%s\n%s" % (name, desc, contents)

    def get_examine_appearance(self, invoker):
        """
        Shows the object as it were examined.
        """
        name = self.get_appearance_name(invoker=invoker)

        attributes_str = ''

        core_attribs = self._odata.keys()
        core_attribs.sort()
        for key in core_attribs:
            attributes_str += ' %s: %s\n' % (key, self._odata[key])

        if self.attributes:
            attributes_str += '\n### EXTRA ATTRIBUTES ###\n'
            
            for key, value in self.attributes.items():
                attributes_str += ' %s: %s\n' % (key, value)

        return "%s\n%s" % (name, attributes_str)

    def contextual_object_search(self, desc):
        """
        Searches for objects using the current object as a frame of
        reference

        :param str desc: A string with which to perform a search

        :rtype: :class:'BaseObject'
        :returns: An object that best matches the string provided
        """
        desc = desc.strip()
        if not desc:
            # Probably an empty string, which we can't do much with.
            return None

        mud_service = self._mud_service

        if desc[0] == '#':
            # Absolute object identifier: lookup the id
            obj = mud_service.object_store.get_object(desc[1:])

            if not self.is_admin():
                location_match = self.location.id == obj.location.id or \
                                 self.location.id == obj.id
            else:
                location_match = True

            if location_match:
                return obj

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

    def after_session_connect_event(self):
        """
        This is called when the proxy authenticates and logs in a Session that
        controls this object. This event is only triggered when the first
        Session controlling this object is logged in. For example, logging in
        a second time with another client would not trigger this again.

        This is currently only meaningful for PlayerObject instances.
        """
        pass

    def after_session_disconnect_event(self):
        """
        This is called when the last Sesssion that controls this object is
        disconnected. If you have two clients open that are authenticated and
        controlling the same object, this will not trigger until the last
        Session is closed.

        This is currently only meaningful for PlayerObject instances.
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
        pass

    #noinspection PyUnusedLocal
    def before_object_enters_event(self, actor):
        """
        Triggered before an object arrives in this object's inventory.

        :param BaseObject actor: The object doing the entering.
        """
        pass

    #noinspection PyUnusedLocal
    def after_object_enters_event(self, actor):
        """
        Triggered after an object physically enters this object's inventory.

        :param BaseObject actor: The object doing the entering.
        """
        pass