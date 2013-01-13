"""
This module contains stuff that is done on the game's first startup.
"""

from twisted.internet.defer import inlineCallbacks
import settings
from src.utils import logger

@inlineCallbacks
def setup_db(store, conn):
    """
    Setup our Postgres database. Do some really basic population.

    :param ObjectStore store:
    """

    yield conn.runOperation(
        """
        CREATE TABLE %s
        (
          id serial NOT NULL,
          data json,
          CONSTRAINT %s_id PRIMARY KEY (id)
        )
        WITH (
          OIDS=FALSE
        );
        """ % (settings.OBJECT_TABLE_NAME, settings.OBJECT_TABLE_NAME)
    )

    logger.info("%s table created." % settings.OBJECT_TABLE_NAME)
    # Now create the starter room.
    parent_path = 'src.game.parents.base_objects.room.RoomObject'
    yield store.create_object(parent_path, name='And so it begins...')