import unittest
from src.server.accounts.in_memory_store import InMemoryAccountStore, PlayerAccount

class DBAccountStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryAccountStore(db_name='dott_accounts_test')

    def tearDown(self):
        #pass
        del self.store._server['dott_accounts_test']

    def test_empty_db_creation(self):
        """
        Makes sure the default DB is created.
        """
        num_objects = len(self.store._db)
        # The DB should be reachable, but empty.
        self.assertEqual(num_objects, 0)

    def test_create_account(self):
        """
        Tests the creation and querying of an account.
        """
        account = PlayerAccount(username='TestGuy', password='yay', email='woot@woot.com')
        self.store.save_account(account)

        num_accounts = len(self.store._db)
        self.assertEqual(num_accounts, 1)

        testguy = self.store.get_account('TestGuy')