"""
Assorted utilities for unit testing.
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
        yield self.object_store.prep_and_load()
        yield self.account_store.prep_and_load()

    #noinspection PyProtectedMember
    def unload(self):
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
        """

        yield self.create_clean_game_env()

    def tearDown(self):
        """
        Delete the created data stores between unit tests.
        """

        self.cleanup_game_env()

    @inlineCallbacks
    def create_clean_game_env(self):
        """
        Creates a fresh set of stores, DBs, and etc.
        """

        conn = psycopg2.connect(user=settings.DATABASE_USERNAME)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
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
        schema_file = os.path.join(settings.BASE_PATH, 'misc', 'dott-schema.sql')
        schema = open(schema_file).read()
        cur.execute(schema)
        cur.close()
        conn.close()

        self.mud_service = MockMudService()
        yield self.mud_service.prep_and_load()
        self.global_cmd_table = self.mud_service.global_cmd_table
        self.command_handler = self.mud_service.command_handler
        self.session_manager = self.mud_service.session_manager
        self.object_store = self.mud_service.object_store
        self.account_store = self.mud_service.account_store

    def cleanup_game_env(self):
        """
        Cleans up the created environment.
        """

        self.mud_service.unload()