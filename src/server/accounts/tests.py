import unittest2
from src.utils.test_utils import DottTestCase
from src.server.accounts.in_memory_store import PlayerAccount
from src.server.accounts.exceptions import UsernameTakenException
from src.server.accounts.validators import is_email_valid, is_username_valid

class DBAccountStoreTests(DottTestCase):
    def test_empty_db_creation(self):
        """
        Makes sure the default DB is created.
        """
        num_objects = len(self.account_store._db)
        # The DB should be reachable, but empty.
        self.assertEqual(num_objects, 0)

    def test_create_account(self):
        """
        Tests the creation and querying of an account.
        """
        account = self.account_store.create_account('TestGuy', 'yay', 'some@guy.com')
        # These two values should be the same. username is just a property
        # that maps to _id.
        self.assertEqual('TestGuy', account.username)
        self.assertEqual('TestGuy', account._id)
        # Make sure the password given at creation is valid.
        self.assertEqual(account.check_password('yay'), True)
        # Change the password.
        account.set_password('flah')
        # Make sure the newly calculated value matches.
        self.assertEqual(account.check_password('flah'), True)
        # Try the old original value and make sure it doesn't match.
        self.assertEqual(account.check_password('yay'), False)

        num_accounts = len(self.account_store._db)
        self.assertEqual(num_accounts, 1)

        # Just make sure it works.
        self.account_store.get_account('TestGuy')

        # Trying to create an account with a username that is already
        # in use.
        self.assertRaises(UsernameTakenException,
                          self.account_store.create_account,
                          'TestGuy', 'yay', 'some@guy.com')

class ValidatorTests(DottTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_email_validator(self):
        """
        Tests the email validation function.
        """
        self.assertTrue(is_email_valid('s@s.com'))
        self.assertTrue(is_email_valid('s@s.co.uk'))
        self.assertTrue(is_email_valid('s+h@s.com'))

        self.assertFalse(is_email_valid('s+h@s.'))
        self.assertFalse(is_email_valid('s@s'))
        self.assertFalse(is_email_valid('s'))

    def test_username_validator(self):
        """
        Tests the username validation function.
        """
        self.assertTrue(is_username_valid('Qt'))
        self.assertTrue(is_username_valid('Hi_there'))
        self.assertTrue(is_username_valid('Space Ghast'))

        self.assertFalse(is_username_valid('Q'))
        self.assertFalse(is_username_valid('Q-'))
        self.assertFalse(is_username_valid('Qs"'))