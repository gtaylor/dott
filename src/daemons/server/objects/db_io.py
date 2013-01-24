"""
This module manages all I/O from the DB, and handles the population of the
InMemoryObjectStore.
"""

import json

from twisted.internet.defer import inlineCallbacks, returnValue

import settings
from src.utils import logger
from src.daemons.server.objects import on_first_run
from src.daemons.server.objects.parent_loader.exceptions import InvalidParent
from src.utils.db import txPGDictConnection


class DBManager(object):
    """
    This class serves as an abstraction layer between the ObjectStore
    and the underlying database. It handles the loading of objects at
    server start time, and all CRUD operations on the DB side. DBManager is
    allowed to manipulate the self.store._objects dict.
    """

    # TODO: Add created_by_id column.
    # TODO: Add a created_dtime column.
    # TODO: Add last_saved_dtime column.
    # TODO: Add home_id column.
    # TODO: Add flags column?

    # This is the base SELECT statement we'll use in a few methods for
    # retrieving one or all object rows. To retrieve a subset, tack on a
    # WHERE clause by string concatenation.
    BASE_OBJECT_SELECT = (
        "SELECT id, name, parent, location_id, base_type,"
        " originally_controlled_by_account_id, controlled_by_account_id,"
        " description, zone_id, aliases, destination_id, data "
        "FROM dott_objects"
    )

    def __init__(self, mud_service, parent_loader, db_name=None):
        """
        :param ParentLoader parent_loader: A reference to a ParentLoader instance.
        :param MudService mud_service: A reference to the top-level MudService.
        :keyword str db_name: Overrides the DB name for the object DB. Currently
            just used for unit testing.
        """

        self._db_name = db_name or settings.DATABASE_NAME
        # This eventually contains a txpostgres Connection object, which is
        # where we can query.
        self._db = None
        self._parent_loader = parent_loader
        self._mud_service = mud_service

    @inlineCallbacks
    def prepare_and_load(self):
        """
        Checks to make sure that the dott_objects table exists. If it doesn't,
        it creates it.

        :rtype: bool
        :returns: True if we had to create the dott_objects table, False if
            it already existed.
        """

        # Instantiate the connection to Postgres.
        self._db = txPGDictConnection()
        yield self._db.connect(
            user=settings.DATABASE_USERNAME,
            database=self._db_name
        )

        # The first time the game is started, the objects table won't be
        # present. Determine whether it exists.
        is_objects_table_present = yield self.is_objects_table_present()
        if not is_objects_table_present:
            # Table is not present, create it.
            on_first_run.setup_db(self._db)
            returnValue(True)
        else:
            returnValue(False)

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
            "  WHERE table_schema='public' AND table_name='dott_objects'"
        )

        returnValue(bool(results))

    @inlineCallbacks
    def load_objects_into_store(self, loader_func):
        """
        Loads all of the objects from the DB into RAM.

        :param function loader_func: The function to run on the instantiated
            BaseObject sub-classes.
        """

        logger.info("Loading objects into store.")

        results = yield self._db.runQuery(self.BASE_OBJECT_SELECT)

        for row in results:
            # Given an object ID and a JSON str, load this object into the store.
            loader_func(self.instantiate_object_from_row(row))

    def instantiate_object_from_row(self, row):
        """
        This loads the parent class, instantiates the object through the
        parent class (passing the values from the DB as constructor kwargs).

        :param row: the txPG row representing this object.
        :rtype: BaseObject
        :returns: The newly loaded object.
        """

        id = row['id']
        doc = json.loads(row['data'])

        # Loads the parent class so we can instantiate the object.
        try:
            parent = self._parent_loader.load_parent(row['parent'])
        except InvalidParent:
            # Get more specific with the exception output in this case. This
            # will give us an object ID to look at in the logs.
            raise InvalidParent(
                'Attempting to load invalid parent on object #%s: %s' % (
                    id,
                    row['parent'],
                )
            )
        # Instantiate the object, using the values from the DB as kwargs.
        return parent(
            self._mud_service,
            **row
        )

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
                "INSERT INTO dott_objects"
                "  (name, parent, location_id, base_type, "
                "   originally_controlled_by_account_id, "
                "   controlled_by_account_id, description, zone_id, "
                "   aliases, destination_id, data) "
                "  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                " RETURNING id",
                (
                    obj.name,
                    obj.parent,
                    obj.location_id,
                    obj.base_type,
                    obj.originally_controlled_by_account_id,
                    obj.controlled_by_account_id,
                    obj.description,
                    obj.zone_id,
                    obj.aliases,
                    obj.destination_id,
                    json.dumps(odata),
                )
            )
            inserted_id = result[0][0]
            obj.id = inserted_id
        else:
            yield self._db.runOperation(
                "UPDATE dott_objects SET "
                "  name=%s,"
                "  parent=%s,"
                "  location_id=%s,"
                "  base_type=%s,"
                "  originally_controlled_by_account_id=%s,"
                "  controlled_by_account_id=%s,"
                "  description=%s,"
                "  zone_id=%s,"
                "  aliases=%s,"
                "  destination_id=%s,"
                "  data=%s "
                " WHERE ID=%s",
                (
                    obj.name,
                    obj.parent,
                    obj.location_id,
                    obj.base_type,
                    obj.originally_controlled_by_account_id,
                    obj.controlled_by_account_id,
                    obj.description,
                    obj.zone_id,
                    obj.aliases,
                    obj.destination_id,
                    json.dumps(odata),
                    obj.id
                )
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

        modified_query = "{base_query} WHERE id=%s".format(
            base_query=self.BASE_OBJECT_SELECT
        )
        results = yield self._db.runQuery(modified_query, (obj.id,))

        for row in results:
            returnValue(self.instantiate_object_from_row(row))
        else:
            returnValue(None)