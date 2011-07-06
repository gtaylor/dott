import couchdb
from couchdb.http import ResourceNotFound
from dott.settings import DATABASES
from dott.src.utils import logger
from dott.src.server.parents.base_objects.room import RoomObject

class InMemoryObjectStore(object):
    def __init__(self, db_name=None):
        self._server = couchdb.Server()
        self._db = None
        self._prep_db(db_name=db_name)
        self._objects = {}
        self._load_objects_into_ram()

    def _prep_db(self, db_name=None):
        if not db_name:
            db_name = DATABASES['objects']['NAME']

        try:
            self._db = self._server[db_name]
        except ResourceNotFound:
            logger.warning('No DB found, creating a new one.')
            self._db = self._server.create(db_name)

        if len(self._db) == 0:
            self._create_initial_room()

    def _load_objects_into_ram(self):
        for doc_id in self._db:
            self._load_object(doc_id)

    def _load_object(self, doc_id):
        doc = self._db[doc_id]
        # TODO: Figure out how to load parent classes in here.
        self._objects[doc_id] = RoomObject(**doc)

    def _create_initial_room(self):
        room = RoomObject(name='And so it begins...')
        self.save_object(room)

    def save_object(self, obj_or_id):
        odata = obj_or_id.odata
        odata['parent'] = '%s.%s' % (obj_or_id.__module__,
                                     obj_or_id.__class__.__name__)
        self._db.save(odata)
