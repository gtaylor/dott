import couchdb
from couchdb.http import ResourceNotFound

from settings import DATABASES
from src.utils import logger
from src.server.parent_loader import PARENT_LOADER

class InMemoryObjectStore(object):
    """
    Serves as an in-memory object store for all "physical" entities in the
    game. An "object" can be stuff like a room or a thing.
    """
    def __init__(self, db_name=None, config_store=None, account_store=None,
                 command_handler=None):
        """
        .. warning:: Due to the order this class is instantiated in
            ``dott.tac``, do not interact with self._account_store within
            this constructor, as it won't be set yet.

        :keyword str db_name: Overrides the DB name for the object DB.
        :keyword InMemoryConfigStore config_store: If specified, override
            the default global config store. This is useful for unit testing.
        """
        self._config_store = config_store
        self._account_store = account_store
        self._command_handler = command_handler

        # Eventually contains a CouchDB reference. Queries come through here.
        self._db = None
        # Keys are CouchDB ids, values are the parent instances (children of
        # src.game.parents.base_objects.base.BaseObject
        self._objects = {}

        # Reference to CouchDB server connection.
        self._server = couchdb.Server()
        # Loads or creates+loads the CouchDB database.
        self._prep_db(db_name=db_name)
        # Loads all of the objects into RAM from CouchDB.
        self._load_objects_into_ram()

    def _prep_db(self, db_name=None):
        """
        Sets the :attr:`_db` reference. Creates the CouchDB if the requested
        one doesn't exist already.

        :keyword str db_name: Overrides the DB name for the object DB.
        """
        if not db_name:
            # Use the default configured DB name for objects DB.
            db_name = DATABASES['objects']['NAME']

        try:
            # Try to get a reference to the CouchDB database.
            self._db = self._server[db_name]
        except ResourceNotFound:
            logger.warning('No DB found, creating a new one.')
            self._db = self._server.create(db_name)

        if not len(self._db):
            # No objects are in this DB. We know the starter room can't
            # exist yet, so create it.
            self._create_initial_room()

    def _load_objects_into_ram(self):
        """
        Loads all of the objects from the DB into RAM.
        """
        for doc_id in self._db:
            self._load_object(doc_id)

    def _load_object(self, doc_id):
        """
        This loads the parent class, instantiates the object through the
        parent class (passing the values from the DB as constructor kwargs).

        :param str doc_id: The CouchDB ID for the object to load.
        """
        # Retrieves the JSON doc from CouchDB.
        doc = self._db[doc_id]
        # Loads the parent class so we can instantiate the object.
        parent = PARENT_LOADER.load_parent(doc['parent'])
        # Instantiate the object, using the values from the DB as kwargs.
        self._objects[doc_id] = parent(
            object_store=self,
            command_handler=self._command_handler,
            **doc
        )

    def _create_initial_room(self):
        """
        If the initial RoomObject that players login to doesn't exist, create
        it and save it. Loading will be done later.
        """
        parent_path = 'src.game.parents.base_objects.room.RoomObject'
        room = self.create_object(parent_path, name='And so it begins...')
        # Sets the newly created room as the room that new players connect to.
        self._config_store.set_value('NEW_PLAYER_ROOM', room.id)

    def create_object(self, parent_path, **kwargs):
        """
        Creates and saves a new object of the specified parent.

        :param str parent_path: The full Python path + class name for a parent.
            for example, src.game.parents.base_objects.room.RoomObject.
        :keyword dict kwargs: Additional attributes to set on the object.
        :rtype: BaseObject
        :returns: The newly created/instantiated/saved object.
        """
        NewObject = PARENT_LOADER.load_parent(parent_path)
        obj = NewObject(
            object_store=self,
            command_handler=self._command_handler,
            parent=parent_path,
            **kwargs
        )
        obj.save()
        return obj

    def save_object(self, obj):
        """
        Saves an object to CouchDB. The _odata attribute on each object is
        the raw dict that gets saved to and loaded from CouchDB.

        :param BaseObject obj: The object to save to the DB.
        """
        odata = obj._odata
        # Saves to CouchDB.
        id, rev = self._db.save(odata)
        # For new objects, update our in-memory object with the newly assigned
        # _id in CouchDB.
        obj._id = id
        # Update our in-memory cache with the saved object.
        self._objects[odata['_id']] = obj

    def get_object(self, obj_id):
        """
        Given an object ID, return the object's instance.

        :param str obj_id: The ID of the object to return.
        :returns: The requested object, which will be a :class:`BaseObject`
            sub-class of some sort.
        """
        return self._objects[obj_id]
