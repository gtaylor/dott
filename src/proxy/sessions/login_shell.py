import datetime
import hashlib

from src.proxy.accounts.validators import is_email_valid, is_username_valid
from src.proxy.accounts.exceptions import AccountNotFoundException
from src.server.commands.interactive import InteractiveShell
from src.server.email import EMAIL_SENDER

class LoginShell(InteractiveShell):
    """
    Handles the login and registration process in an interactive manner.

    :attr callable current_step: The callable that all user input is piped
        through. This is the current step of login/registration.
    :attr str username_given: The username the client connecting provided.
    :attr str email_given: For new characters, the email address the client
        connecting provided.
    :attr PlayerAccount matched_account: If a user enters a username that
        matches an existing account, this gets set so we can check to see
        if they provide a valid password.
    :attr str generated_password: For new accounts, the randomly generated
        password to be emailed.
    """
    def __init__(self, *args, **kwargs):
        super(LoginShell, self).__init__(*args, **kwargs)

        self.current_step = self.step_get_username
        self.username_given = None
        self.matched_account = None
        self.email_given = None
        self.generated_password = None

    @property
    def _account_store(self):
        """
        Short-cut to the global account store.

        :rtype: InMemoryAccountStore
        :returns: Reference to the global account store instance.
        """
        return self.session._account_store

    def process_input(self, user_input):
        """
        Regardless of which step they're on, this method cleanses input and
        hands off to whatever callable is set as the current step.
        """
        cleaned_input = user_input.strip()
        
        self.current_step(cleaned_input)

    def prompt_get_username(self):
        """
        The username promp to be sent to the player.
        """
        self.session.msg('Enter your name:')

    def step_get_username(self, user_input):
        """
        Processes the player's response to the username prompt.

        :param str user_input: The username the player entered.
        """
        if not user_input:
            # Probably just hit enter. Ask again.
            self.prompt_get_username()
            return False

        if not is_username_valid(user_input):
            self.session.msg(
                'Invalid username given. Usernames must be at least two '\
                'characters long, no greater than 25, and must only contain '\
                'alphanumerics, spaces, and underscores.\n'
            )
            self.prompt_get_username()
            return False

        # At this point, username is valid.
        self.username_given = user_input
        
        try:
            # See if there's an account match.
            self.matched_account = self._account_store.get_account(self.username_given)
        except AccountNotFoundException:
            # No account match, must be a new player.
            self.current_step = self.step_confirm_new_username
            self.prompt_confirm_new_username()
            return False

        self.current_step = self.step_get_existing_user_password
        self.prompt_get_existing_user_password()
        return True

    def prompt_get_existing_user_password(self):
        """
        Ask an existing user for their password.
        """
        self.session.msg("Enter your password:")

    def step_get_existing_user_password(self, user_input):
        """
        Retrieve and check an existing user's password.
        """
        if not user_input:
            self.prompt_get_existing_user_password()
            return False

        if self.matched_account.check_password(user_input):
            self.session.msg("You are now logged in.")
            self.session.login(self.matched_account)
        else:
            self.session.msg("Invalid password specified. Login attempt logged.\n")
            self.current_step = self.step_get_username
            self.prompt_get_username()
            return False

    def prompt_confirm_new_username(self):
        """
        Ask the user whether they're new, or mis-typed a username.
        """
        self.session.msg("We haven't seen anyone called %s yet, are you a new player? (Y/N)" % self.username_given)

    def step_confirm_new_username(self, user_input):
        """
        There's no username matching the user's input, ask them if they are
        new, or merely mis-typed a username.

        :param str user_input: The user's response to whether they are new (Y)
            or not (N).
        """
        if user_input not in ['Y', 'y', 'N', 'n']:
            # Something other than y/n. Ask again.
            self.prompt_confirm_new_username()
            return False

        if user_input.lower() == 'n':
            # User is not new. Must have just fat-fingered something. Send
            # them back to the username step.
            self.current_step = self.step_get_username
            self.username_given = None
            self.prompt_get_username()
            return True

        # New player, start gathering email address for password generation.
        self.prompt_get_email_address_1()
        self.current_step = self.step_get_email_address_1
        return True

    def prompt_get_email_address_1(self):
        """
        Explains why we ask for email addresses.
        """
        message = "We use your email address to send you a generated password. "\
                  "You may then login and leave it, or change it to whatever "\
                  "you'd like. If you end up needing to reset your password, "\
                  "the email address you provide here will be the key.\n\n"\
                  "What is your email address?:"
        self.session.msg(message)

    def step_get_email_address_1(self, user_input):
        """
        Validate and store the user-provided email address.

        :param str user_input: The email address the user specifies.
        """
        if not user_input or not is_email_valid(user_input):
            self.session.msg('Invalid email address.\n')
            self.prompt_get_email_address_1()
            return False

        # Valid email address, ask again to verify.
        self.prompt_get_email_address_2()
        self.email_given = user_input
        self.current_step = self.step_get_email_address_2
        return True

    def prompt_get_email_address_2(self):
        """
        Make them re-type the email address, just in case.
        """
        message = "Please enter your email address again for verification:"
        self.session.msg(message)

    def step_get_email_address_2(self, user_input):
        """
        Make sure the second typing of email address matches the first. If
        so,
        """
        if user_input != self.email_given:
            self.session.msg("Your email addresses didn't match.\n")
            self.prompt_get_email_address_1()
            self.current_step = self.step_get_email_address_1
            return False

        # Email address matches, create the account.
        self._create_new_account()
        return True

    def _create_new_account(self):
        """
        Ties together various things to create the account, send their
        randomly generated password, and boot their ass off.
        """
        self.generated_password = self._generate_password()
        self._send_registration_mail()
        self._create_account()
        self.session.msg(
            "Your account has been created, and your randomly "\
            "generated password has been sent to %s. Please "\
            "check your mail, find the password, and re-connect.\n" %
            self.email_given)
        self.session.msg("Disconnecting...")
        self.session.disconnect_client()

    def _send_registration_mail(self):
        """
        Shoots out a rough email to the user letting them know to re-connect
        with the given user/pass.
        """
        subject = 'Welcome to Dawn of the Titans!'
        body = "Greetings,\n\n"\
               "An account has been created for you with the following "\
               "credentials:\n\n"\
               "Username: %s\nPassword: %s\n\n"\
               "You may connect to the game with your choice of MUD client at:\n\n"\
               "gc-taylor.com, port 4000" % (
            self.username_given,
            self.generated_password,
        )

        # Bombs away.
        EMAIL_SENDER.send_email(
            subject,
            body,
            [self.email_given]
        )

    def _create_account(self):
        """
        Creates the user's new account with the given info, and the randomly
        generated password.
        """
        self._account_store.create_account(
            self.username_given,
            self.generated_password,
            self.email_given)

    def _generate_password(self):
        """
        Creates a hash, lops off the first few characters, and that's a
        random password to hand the user.

        :rtype: str
        :returns: A 'randomly' generated password.
        """
        input = '%s%s' % (datetime.datetime.now(), self.username_given)
        return hashlib.sha512(input).hexdigest()[:5]
