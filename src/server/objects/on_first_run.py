"""
This module contains stuff that is done on the game's first startup.
"""

from src.server.objects import defines
from src.utils import logger

def setup_db(pool):
    """
    Setup our sqlite database
    """

    def post_create_cb(txn):
        logger.info("Table created: %s" % defines.DB_OBJECTS_TABLE)

    pool.runOperation(
        "CREATE TABLE %s (dbref INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT)" % defines.DB_OBJECTS_TABLE
    ).addCallback(post_create_cb)