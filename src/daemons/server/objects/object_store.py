from fuzzywuzzy import fuzz
from twisted.internet.defer import inlineCallbacks, returnValue

#from src.utils import logger
from src.daemons.server.objects.db_io import DBManager
from src.daemons.server.objects.exceptions import InvalidObjectId
from src.daemons.server.objects.parent_loader.loader import ParentLoader


class ObjectStore(object):
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
        :param MudService mud_service: The MudService class running the game.
        :keyword str db_name: Overrides the DB name for the object DB. Currently
            just used for unit testing.
        """

        self._mud_service = mud_service
        # This is used to sub-classes of BaseObject.
        self.parent_loader = ParentLoader()

        # Keys are object IDs, values are the parent instances (children of
        # src.game.parents.base_objects.base.BaseObject)
        self._objects = {}

        # DB abstraction layer.
        self.db_manager = DBManager(
            mud_service, self.parent_loader, db_name=db_name
        )

    @inlineCallbacks
    def prep_and_load(self):
        """
        This runs early in server startup. Calls on the DBManager
        (self.db_manager) to prep the DB and load all objects.
        """

        is_first_run = yield self.db_manager.prepare_and_load()
        if is_first_run:
            # If this is the first time the server has been started, we'll
            # need to create the starter room.
            parent_path = 'src.game.parents.base_objects.room.RoomObject'
            yield self.create_object(parent_path, name='And so it begins...')

        def loader_func(obj):
            """
            This function runs on each object instantiated from the DB at
            start time.

            :param BaseObject obj: The object to load into the store.
            """
            self._objects[obj.id] = obj

        yield self.db_manager.load_objects_into_store(loader_func)

    @inlineCallbacks
    def create_object(self, parent_path, name, **kwargs):
        """
        Creates and saves a new object of the specified parent.

        :param str parent_path: The full Python path + class name for a parent.
            for example, src.game.parents.base_objects.room.RoomObject.
        :param str name: The name of the object.
        :keyword dict kwargs: Additional attributes to set on the object.
        :rtype: BaseObject
        :returns: The newly created/instantiated/saved object.
        """

        # TODO: Parameterize some of this?

        NewObject = self.parent_loader.load_parent(parent_path)
        obj = NewObject(
            self._mud_service,
            id=None,
            parent=parent_path,
            **kwargs
        )
        obj = yield self.save_object(obj)

        returnValue(obj)

    @inlineCallbacks
    def save_object(self, obj):
        """
        Saves an object to the DB.

        :param BaseObject obj: The object to save to the DB.
        """

        saved_obj = yield self.db_manager.save_object(obj)
        self._objects[saved_obj.id] = saved_obj
        returnValue(saved_obj)

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

        reloaded_obj = yield self.db_manager.reload_object(obj)
        self._objects[reloaded_obj.id] = reloaded_obj
        returnValue(reloaded_obj)

    def get_object(self, obj_id):
        """
        Given an object ID, return the object's instance.

        :param str obj_id: The ID of the object to return.
        :returns: The requested object, which will be a :class:`BaseObject`
            sub-class of some sort.
        :raises: :py:exc:`src.server.objects.exceptions.InvalidObjectId` if
            no object with the requested ID exists.
        """

        assert isinstance(obj_id, int), \
            "get_object had a non-int passed: %s %s" % (obj_id, type(obj_id))

        try:
            return self._objects[obj_id]
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