"""
Account store tests.
"""

from twisted.internet.defer import inlineCallbacks

from src.utils.test_utils import DottTestCase
from src.accounts.exceptions import UsernameTakenException
from src.accounts.validators import is_email_valid, is_username_valid


class DBAccountStoreTests(DottTestCase):

    @inlineCallbacks
    def test_create_account(self):
        """
        Tests the creation and querying of an account.

        TODO: RESTORE THIS TEST TO WORKING CONDITION
        """

        account = yield self.account_store.create_account('TestGuy', 'yay', 'some@guy.com')

        # These two values should be the same. username is just a property
        # that maps to _id.
        self.assertEqual(account.username, 'TestGuy')

        # Make sure the password given at creation is valid.
        self.assertEqual(account.check_password('yay'), True)
        # Change the password.
        account.set_password('flah')
        # Make sure the newly calculated value matches.
        self.assertEqual(account.check_password('flah'), True)
        # Try the old original value and make sure it doesn't match.
        self.assertEqual(account.check_password('yay'), False)

        num_accounts = yield self.account_store.get_account_count()
        self.assertEqual(num_accounts, 1)

        # Just make sure it works.
        q_account = yield self.account_store.get_account_by_username('TestGuy')
        self.assertEqual(q_account.username, 'TestGuy')

        # Trying to create an account with a username that is already
        # in use.
        try:
            yield self.account_store.create_account('TestGuy', 'yay', 'some@guy.com')
            self.fail("This should have failed due to duplication.")
        except UsernameTakenException:
            pass


class ValidatorTests(DottTestCase):
    """
    Tests some account-related validators. These mostly come into play
    during registration and login, but they are of general use.
    """

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