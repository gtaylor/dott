"""
This module manages all I/O from the DB, and handles the population of the
InMemoryObjectStore.
"""

from psycopg2.extras import Json

from twisted.internet.defer import inlineCallbacks, returnValue

import settings
from src.utils import logger
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
        "SELECT id, name, parent, location_id,"
        " originally_controlled_by_account_id, controlled_by_account_id,"
        " description, internal_description, zone_id, aliases, destination_id, "
        " attributes "
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
        Gets a connection set up.
        """

        # Instantiate the connection to Postgres.
        self._db = txPGDictConnection()
        yield self._db.connect(
            user=settings.DATABASE_USERNAME,
            database=self._db_name
        )

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

        # psycopg2 handles the JSON adaptation.
        row['attributes'] = row['attributes'] or {}

        # Loads the parent class so we can instantiate the object.
        try:
            parent = self._parent_loader.load_parent(row['parent'])
        except InvalidParent:
            # Get more specific with the exception output in this case. This
            # will give us an object ID to look at in the logs.
            raise InvalidParent(
                'Attempting to load invalid parent on object #%s: %s' % (
                    row['id'],
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
        Saves an object to the DB. The ``attributes`` attribute on each object is
        the raw dict that gets saved to and loaded from the DB entry.

        :param BaseObject obj: The object to save to the DB.
        """

        attributes = obj.attributes

        if not obj.id:
            result = yield self._db.runQuery(
                "INSERT INTO dott_objects"
                "  (name, parent, location_id, base_type, "
                "   originally_controlled_by_account_id, "
                "   controlled_by_account_id, description, zone_id, "
                "   aliases, destination_id, internal_description, attributes) "
                "  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
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
                    obj.internal_description,
                    Json(attributes),
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
                "  internal_description=%s,"
                "  attributes=%s "
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
                    obj.internal_description,
                    Json(attributes),
                    obj.id
                )
            )
        returnValue(obj)

    @inlineCallbacks
    def destroy_object(self, obj):
        """
        Deletes an object from the DB.

        :param BaseObject obj: The object to delete in the DB.
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