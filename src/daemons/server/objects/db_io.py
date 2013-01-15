"""
This module manages all I/O from the DB, and handles the population of the
InMemoryObjectStore.
"""

import json

from txpostgres import txpostgres
from twisted.internet.defer import inlineCallbacks, returnValue

import settings
from src.utils import logger
from src.daemons.server.objects import on_first_run
from src.daemons.server.parent_loader.exceptions import InvalidParent

class DBManager(object):
    """
    This class serves as an abstraction layer between the InMemoryObjectStore
    and the underlying database. It handles the loading of objects at
    server start time, and all CRUD operations on the DB side. DBManager is
    allowed to manipulate the self.store._objects dict.
    """

    def __init__(self, store, db_name=None):
        """
        :keyword InMemoryObjectStore store: The object store this instance
            manages.
        :keyword str db_name: Overrides the DB name for the object DB. Currently
            just used for unit testing.
        """

        self.store = store

        self._db_name = db_name or settings.DATABASE_NAME
        # This eventually contains a txpostgres Connection object, which is
        # where we can query.
        self._db = None

    @inlineCallbacks
    def prepare_and_load(self):
        """
        Prepares the store for duty, then loads all objects from the DB into
        the object store.
        """

        # Instantiate the connection to Postgres.
        self._db = txpostgres.Connection()
        yield self._db.connect(
            user=settings.DATABASE_USERNAME,
            database=self._db_name
        )

        # The first time the game is started, the objects table won't be
        # present. Determine whether it exists.
        is_objects_table_present = yield self.is_objects_table_present()
        if not is_objects_table_present:
            # Table is not present, create it.
            on_first_run.setup_db(self.store, self._db)
        else:
            # Table was present, load the whole shebang into the store.
            self.load_objects_into_store()

    @inlineCallbacks
    def is_objects_table_present(self):
        """
        Sets the :attr:`_db` reference. Does some basic DB population if
        need be.

        :rtype: bool
        :returns: True if the dott_objects table is present, False if not.
        """

        # See if the dott_objects table already exists. If not, create it.
        results = yield self._db.runQuery(
            "SELECT table_name FROM information_schema.tables"
            "  WHERE table_schema='public' AND table_name=dott_objects"
        )

        returnValue(bool(results))

    @inlineCallbacks
    def load_objects_into_store(self):
        """
        Loads all of the objects from the DB into RAM.
        """

        logger.info("Loading objects into store.")

        results = yield self._db.runQuery("SELECT * FROM dott_objects")

        for oid, ojson_str in results:
            # Given an object ID and a JSON str, load this object into the store.
            self.load_object(oid, ojson_str)

    def load_object(self, oid, ojson_str):
        """
        This loads the parent class, instantiates the object through the
        parent class (passing the values from the DB as constructor kwargs).

        :param oid:
        :param ojson_str:
        :rtype: BaseObject
        :returns: The newly loaded object.
        """

        doc = json.loads(ojson_str)

        # Loads the parent class so we can instantiate the object.
        try:
            parent = self.store._parent_loader.load_parent(doc['parent'])
        except InvalidParent:
            # Get more specific with the exception output in this case. This
            # will give us an object ID to look at in the logs.
            raise InvalidParent(
                'Attempting to load invalid parent on object #%s: %s' % (
                    oid,
                    doc['parent'],
                )
            )
            # Instantiate the object, using the values from the DB as kwargs.
        self.store._objects[oid] = parent(self.store._mud_service, id=oid, **doc)
        return self.store._objects[oid]

    @inlineCallbacks
    def save_object(self, obj):
        """
        Saves an object to the DB. The _odata attribute on each object is
        the raw dict that gets saved to and loaded from the DB entry.

        :param BaseObject obj: The object to save to the DB.
        """

        odata = obj._odata

        if not obj.id:
            result = yield self._db.runQuery(
                """
                INSERT INTO dott_objects (data) VALUES (%s) RETURNING id
                """, (json.dumps(odata),)
            )
            inserted_id = result[0][0]
            obj.id = inserted_id
        else:
            yield self._db.runOperation(
                """
                UPDATE dott_objects SET data=%s WHERE ID=%s
                """, (json.dumps(odata), obj.id)
            )
        returnValue(obj)

    @inlineCallbacks
    def destroy_object(self, obj):
        """
        Destroys an object by yanking it from :py:attr:`_objects` and the DB.
        """

        yield self._db.runOperation(
            "DELETE FROM dott_objects WHERE id=%s", (obj.id,)
        )


    @inlineCallbacks
    def reload_object(self, obj):
        """
        Re-loads the object from the DB.

        :param BaseObject obj: The object to re-load from the DB.
        :rtype: BaseObject
        :returns: The newly re-loaded object.
        """

        obj_id = obj.id

        results = yield self._db.runQuery(
            "SELECT * FROM dott_objects WHERE id=%s", (obj.id,)
        )

        logger.info("Reloading object from RAM. %s" % results)
        for oid, ojson_str in results:
            del self.store._objects[obj_id]
            self.load_object(oid, ojson_str)
            returnValue(self.load_object(oid, ojson_str))