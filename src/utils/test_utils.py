"""
Assorted utilities for unit testing. Lots of assorted unholy stuff going on
in here, so not for the faint of heart.
"""

import os

import psycopg2
from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks

import settings
from src.game.commands.global_cmdtable import GlobalCommandTable, GlobalAdminCommandTable
from src.daemons.server.commands.handler import CommandHandler
from src.daemons.server.objects.object_store import ObjectStore
from src.accounts.account_store import AccountStore
from src.daemons.proxy.sessions.session_manager import SessionManager

# I'm probably going to hell for this, but we use it to make sure that
# we only create the test DB once, instead of between every test. Makes things
# run a little faster.
DB_WAS_CREATED = False


#noinspection PyDocstring,PyPep8Naming
class FakeProxyAMP(object):
    """
    Fake AMP protocol instance.
    """

    def callRemote(self, *args, **kwargs):
        pass


class MockMudService(object):
    """
    Mocks up the MudService class found in dott.tac.
    """

    #noinspection PyTypeChecker
    def __init__(self):
        self.global_cmd_table = GlobalCommandTable()
        self.global_admin_cmd_table = GlobalAdminCommandTable()
        self.command_handler = CommandHandler(self)
        self.session_manager = SessionManager(self)
        self.object_store = ObjectStore(self, db_name='dott_test')
        self.account_store = AccountStore(db_name='dott_test')
        self.proxyamp = FakeProxyAMP()

    @inlineCallbacks
    def prep_and_load(self):
        """
        Gets the various stores and other stuff set up and loaded from the DB.
        """

        yield self.object_store.prep_and_load()
        yield self.account_store.prep_and_load()

    #noinspection PyProtectedMember
    @inlineCallbacks
    def unload(self):
        """
        Right now this is specific to unit tests, and doesn't actually exist
        in the actual MudService class. We clear out the various test tables
        and close all DB pointers.
        """

        yield self.object_store.db_manager._db.runOperation(
            "TRUNCATE dott_accounts, dott_objects")

        self.object_store.db_manager._db.close()
        self.account_store.db_manager._db.close()


#noinspection PyPep8Naming
class DottTestCase(unittest.TestCase):
    """
    Some helpers for unit testing.
    """

    @inlineCallbacks
    def setUp(self):
        """
        By default, create a bare minimal set of data stores.

        .. note:: If you override this, you'll need to make sure that your
            new method returns a deferred. yield super() if inlinecallbacks.
        """

        yield self.create_clean_game_env()

    @inlineCallbacks
    def tearDown(self):
        """
        Cleans up the created environment.

        .. note:: If you override this, you'll need to make sure that your
            new method returns a deferred. yield super() if inlinecallbacks.
        """

        yield self.mud_service.unload()

    @inlineCallbacks
    def create_clean_game_env(self):
        """
        Creates a fresh set of stores, DBs, and etc.
        """

        global DB_WAS_CREATED
        if not DB_WAS_CREATED:
            # We have to use psycopg2 directly since txpostgres can't
            # be used with autocommit=True.
            conn = psycopg2.connect(user=settings.DATABASE_USERNAME)
            conn.set_session(autocommit=True)
            cur = conn.cursor()
            # Destroy and re-create the test DB to make sure the
            # schema is current.
            cur.execute("DROP DATABASE IF EXISTS %s;" % settings.TEST_DATABASE_NAME)
            cur.execute("CREATE DATABASE %s WITH OWNER=%s;" % (
                settings.TEST_DATABASE_NAME, settings.TEST_DATABASE_USERNAME
            ))
            cur.close()
            conn.close()

            conn = psycopg2.connect(
                user=settings.DATABASE_USERNAME, database=settings.TEST_DATABASE_NAME)
            conn.set_session(autocommit=True)
            cur = conn.cursor()
            # Load the schema from the export.
            schema_file = os.path.join(settings.BASE_PATH, 'misc', 'dott-schema.sql')
            schema = open(schema_file).read()
            cur.execute(schema)
            cur.close()
            conn.close()
            DB_WAS_CREATED = True

        self.mud_service = MockMudService()
        yield self.mud_service.prep_and_load()
        self.global_cmd_table = self.mud_service.global_cmd_table
        self.command_handler = self.mud_service.command_handler
        self.session_manager = self.mud_service.session_manager
        self.object_store = self.mud_service.object_store
        self.account_store = self.mud_service.account_store
