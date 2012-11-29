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
    """

    yield conn.runOperation(
        """
        CREATE TABLE %s
        (
          username character varying(30) NOT NULL,
          data json,
          CONSTRAINT %s_username PRIMARY KEY (username)
        )
        WITH (
          OIDS=FALSE
        );
        """ % (settings.ACCOUNT_TABLE_NAME, settings.ACCOUNT_TABLE_NAME)
    )

    logger.info("%s table created." % settings.ACCOUNT_TABLE_NAME)