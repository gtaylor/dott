"""
This module contains stuff that is done on the game's first startup.
"""

import sqlite3
import settings
from src.proxy.accounts import defines

def setup_db():
    """
    Setup our sqlite database.
    """

    conn = sqlite3.connect(settings.DATABASE_PATH)
    curs = conn.cursor()
    curs.execute(
        "CREATE TABLE %s (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT)" % defines.DB_ACCOUNTS_TABLE
    )
    conn.commit()
    curs.close()