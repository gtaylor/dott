from fuzzywuzzy import fuzz
from twisted.internet.defer import inlineCallbacks

from src.server.objects.db_io import DBManager
from src.server.objects.exceptions import InvalidObjectId

class InMemoryObjectStore(object):
    """
    Serves as an in-memory object store for all "physical" entities in the
    game. An "object" can be stuff like a room or a thing.

    Objects are persisted to a DB via the :py:attr:`db_manager` attribute,
    which is a reference to a :py:class:`src.server.objects.db_io.DBManager`
    instance.

    .. note:: This class should know nothing about the DB that backs it.
        Make sure to keep any DB-related things out of here.
    """

    def __init__(self, mud_service, db_name=None):
        """
        .. warning:: Due to the order this class is instantiated in
            ``dott.tac``, do not interact with self._account_store within
            this constructor, as it won't be set yet.

        :param MudService mud_service: The MudService class running the game.
        :keyword str db_name: Overrides the DB name for the object DB. Currently
            just used for unit testing.
        """

        self._mud_service = mud_service
        # Reference to the server's parent loader instance.
        self._parent_loader = mud_service.parent_loader

        # Keys are object IDs, values are the parent instances (children of
        # src.game.parents.base_objects.base.BaseObject)
        self._objects = {}

        # Kind of silly, but we manually keep track of the next ID.
        self._next_id = 1

        self.db_manager = DBManager(self, db_name=db_name)

    @property
    def _session_manager(self):
        """
        Short-cut to the global session manager.

        :rtype: SessionManager
        :returns: Reference to the global session manager instance.
        """

        #noinspection PyUnresolvedReferences
        return self._mud_service.session_manager

    @property
    def _account_store(self):
        """
        Short-cut to the global account store.

        :rtype: InMemoryAccountStore
        :returns: Reference to the global account store instance.
        """

        #noinspection PyUnresolvedReferences
        return self._mud_service.account_store

    @property
    def _command_handler(self):
        """
        Short-cut to the global command handler.

        :rtype: CommandHandler
        :returns: Reference to the global command handler instance.
        """

        return self._mud_service.command_handler

    def prep_and_load(self):
        """
        This runs early in server startup. Calls on the DBManager (self.db_manager)
        to prep the DB and load all objects.
        """

        self.db_manager.prepare_and_load()

    def create_object(self, parent_path, **kwargs):
        """
        Creates and saves a new object of the specified parent.

        :param str parent_path: The full Python path + class name for a parent.
            for example, src.game.parents.base_objects.room.RoomObject.
        :keyword dict kwargs: Additional attributes to set on the object.
        :rtype: BaseObject
        :returns: The newly created/instantiated/saved object.
        """

        NewObject = self._parent_loader.load_parent(parent_path)
        obj = NewObject(
            self._mud_service,
            _id=self._next_id,
            parent=parent_path,
            **kwargs
        )
        obj.save()
        # Increment the next ID counter for the next object.
        self._next_id += 1
        return obj

    @inlineCallbacks
    def save_object(self, obj):
        """
        Saves an object to the DB.

        :param BaseObject obj: The object to save to the DB.
        """

        yield self.db_manager.save_object(obj)

        # Update our in-memory cache with the saved object.
        self._objects[obj.id] = obj

    @inlineCallbacks
    def destroy_object(self, obj):
        """
        Destroys an object by yanking it from :py:attr:`_objects` and the DB.
        """

        yield self.db_manager.destroy_object(obj)

        # Clear the object out of the store, mark it for GC.
        del self._objects[obj.id]
        del obj

    @inlineCallbacks
    def reload_object(self, obj):
        """
        Re-loads the object from the DB.

        :param BaseObject obj: The object to re-load from the DB.
        :rtype: BaseObject
        :returns: The newly re-loaded object.
        """

        yield self.db_manager.reload_object(obj)

    def get_object(self, obj_id):
        """
        Given an object ID, return the object's instance.

        :param str obj_id: The ID of the object to return.
        :returns: The requested object, which will be a :class:`BaseObject`
            sub-class of some sort.
        :raises: :py:exc:`src.server.objects.exceptions.InvalidObjectId` if
            no object with the requested ID exists.
        """

        try:
            return self._objects[str(obj_id)]
        except KeyError:
            raise InvalidObjectId(
                'Invalid object ID requested: %s' % str(obj_id)
            )

    def get_object_contents(self, obj):
        """
        Returns all objects inside of the specified object.

        :param BaseObject obj: The object whose contents to calculate.
        :rtype: list
        :returns: A list of BaseObject instances whose current location
            is ``obj``.
        """

        return [omatch for omatch in self._objects.values() if omatch.location == obj]

    def global_name_search(self, name):
        """
        Does a global name search of all objects. Compares input to the name
        odata key on all objects.

        :param str name: The name to search for.
        :returns: A generator of ``BaseObject`` matches.
        """

        for id, obj in self._objects.iteritems():
            ratio = fuzz.partial_ratio(name, obj.name)
            if ratio > 50:
                yield obj

    def find_exits_linked_to_obj(self, obj):
        """
        Finds all exits that are linked to the given object.

        :param BaseObject obj: The object which to find linked exits to.
        :rtype: list
        :return: A list of exits that are linked to the given object.
        """

        if obj.base_type == 'exit':
            # Exits can't be linked to one another, this ends up being invalid.
            return []

        # We could use a generator for this, but then we couldn't iterate
        # and delete as we went, as this would change the size of self._objects
        # during the iteration (causing an exception). So store in list.
        linked_exits = []
        for id, db_obj in self._objects.iteritems():
            if not db_obj.base_type == 'exit':
                # Not an exit, not interested.
                continue

            destination = db_obj.destination
            if destination and destination.id == obj.id:
                # This object's destination matches the specified object's ID.
                linked_exits.append(db_obj)

        return linked_exits

    def find_objects_in_zone(self, obj):
        """
        Finds all objects whose zone master object is set to the given object.

        :param BaseObject obj: The object whose zone members to find.
        :rtype: list
        :return: A list of the object's zone members.
        """

        # We could use a generator for this, but then we couldn't iterate
        # and delete as we went, as this would change the size of self._objects
        # during the iteration (causing an exception). So store in list.
        zone_members = []
        for id, db_obj in self._objects.iteritems():
            zone = db_obj.zone
            if zone and zone.id == obj.id:
                # This object's zone matches the specified object's ID.
                zone_members.append(db_obj)

        return zone_members