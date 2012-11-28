"""
This module contains stuff that is done on the game's first startup.
"""

from twisted.internet.defer import inlineCallbacks
from src.utils import logger

@inlineCallbacks
def setup_db(store, conn):
    """
    Setup our Postgres database. Do some really basic population.
    """

    yield conn.runOperation(
        """
        CREATE TABLE dott_objects
        (
          dbref integer NOT NULL,
          data json,
          CONSTRAINT dott_objects_dbref PRIMARY KEY (dbref)
        )
        WITH (
          OIDS=FALSE
        );
        """
    )

    logger.info("dott_objects table created.")
    # Now create the starter room.
    parent_path = 'src.game.parents.base_objects.room.RoomObject'
    store.create_object(parent_path, name='And so it begins...')