"""
This module manages all I/O from the DB, and handles the population of the
AccountStore.
"""

import json

from txpostgres import txpostgres
from twisted.internet.defer import inlineCallbacks, returnValue

import settings
from src.proxy.accounts.account import PlayerAccount
from src.utils import logger
from src.proxy.accounts import on_first_run


class DBManager(object):
    """
    This class serves as an abstraction layer between the AccountStore
    and the underlying database. It handles the loading of objects at
    server start time, and all CRUD operations on the DB side. DBManager is
    allowed to manipulate the self.store._objects dict.
    """

    def __init__(self, store, db_name=None):
        """
        :keyword AccountStore store: The account store this instance manages.
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

        # Just in case this is a code reload.
        self.store._accounts = {}
        # Instantiate the connection to Postgres.
        self._db = txpostgres.Connection()
        yield self._db.connect(
            user=settings.DATABASE_USERNAME,
            database=self._db_name
        )

        # The first time the game is started, the objects table won't be
        # present. Determine whether it exists.
        is_accounts_table_present = yield self.is_accounts_table_present()
        if not is_accounts_table_present:
            on_first_run.setup_db(self.store, self._db)
        else:
            self.load_accounts_into_store()

    @inlineCallbacks
    def is_accounts_table_present(self):
        """
        Sets the :attr:`_db` reference. Does some basic DB population if
        need be.

        :rtype: bool
        :returns: True if the dott_accounts table is present, False if not.
        """

        # See if the dott_accounts table already exists. If not, create it.
        results = yield self._db.runQuery(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name=%s",
            (settings.ACCOUNT_TABLE_NAME,)
        )

        returnValue(bool(results))

    @inlineCallbacks
    def load_accounts_into_store(self):
        """
        Loads all of the objects from the DB into RAM.
        """

        logger.info("Loading accounts into RAM.")

        results = yield self._db.runQuery("SELECT username, data FROM %s"% settings.ACCOUNT_TABLE_NAME)

        for row in results:
            username = row[0]

            self.store._accounts[username.lower()] = self.instantiate_account_from_row(row)

    def instantiate_account_from_row(self, row):
        """
        Given a txpostgres row, return a PlayerAccount instance for it.

        :param row:
        :rtype: PlayerAccount
        :returns: The newly loaded player account.
        """

        username, json_str = row
        doc = json.loads(json_str)
        # Instantiate the object, using the values from the DB as kwargs.
        return PlayerAccount(self.store._mud_service, **doc)

    @inlineCallbacks
    def save_account(self, account):
        """
        Saves an object to the DB. The _odata attribute on each object is
        the raw dict that gets saved to and loaded from the DB entry.

        :param BaseObject obj: The object to save to the DB.
        """

        odata = account._odata
        username = odata['_id'].lower()

        logger.info("Saving new account")
        yield self._db.runOperation(
            """
            INSERT INTO dott_accounts (username, data) VALUES (%s, %s)
            """, (username, json.dumps(odata))
        )
        # TODO: This doesn't support updates.
        returnValue(account)

    @inlineCallbacks
    def destroy_account(self, account):
        """
        Destroys an account.
        """

        yield self._db.runOperation(
            "DELETE FROM dott_accounts WHERE username=%s", (account.username,)
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