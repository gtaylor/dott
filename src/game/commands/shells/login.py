from src.server.commands.interactive import InteractiveShell
from src.server.accounts import ACCOUNT_STORE
from src.server.accounts.exceptions import AccountNotFoundException
from src.server.email import EMAIL_SENDER

class LoginShell(InteractiveShell):
    """
    Handles the login and registration process in an interactive manner.
    """
    def __init__(self, *args, **kwargs):
        super(LoginShell, self).__init__(*args, **kwargs)

        self.current_step = self.step_match_username
        self.username_given = None
        self.email_given = None

    def process_input(self, user_input):
        cleaned_input = user_input.strip()
        
        self.current_step(cleaned_input)

    def prompt_ask_username(self):
        self.session.msg('Enter your name:')

    def step_match_username(self, user_input):
        if not user_input:
            self.prompt_ask_username()
            return

        try:
            account = ACCOUNT_STORE.get_account(user_input)
        except AccountNotFoundException:
            self.username_given = user_input
            self.current_step = self.step_get_new_username
            self.prompt_get_new_username()

    def prompt_get_new_username(self):
        self.session.msg("We haven't seen anyone called %s yet, are you a new player? (Y/N)" % self.username_given)

    def step_get_new_username(self, user_input):
        if user_input not in ['Y', 'y', 'N', 'n']:
            self.prompt_get_new_username()
            return

        if user_input.lower() == 'n':
            self.current_step = self.step_match_username
            self.username_given = None
            self.prompt_ask_username()
            return

        self.prompt_get_email_address_1()
        self.current_step = self.step_get_email_address_1

    def prompt_get_email_address_1(self):
        message = "We use your email address to send you a generated password. "\
                  "You may then login and leave it, or change it to whatever "\
                  "you'd like. If you end up needing to reset your password, "\
                  "the email address you provide here will be the key.\n\n"\
                  "What is your email address?:"
        self.session.msg(message)

    def step_get_email_address_1(self, user_input):
        if not user_input:
            self.prompt_get_email_address_1()
            return

        self.prompt_get_email_address_2()
        self.username_given = user_input
        self.current_step = self.step_get_email_address_2

    def prompt_get_email_address_2(self):
        message = "Please enter your email address again for verification:"
        self.session.msg(message)

    def step_get_email_address_2(self, user_input):
        if not user_input:
            self.prompt_get_email_address_2()
            return

        if user_input != self.username_given:
            self.session.msg("Your email addresses didn't match.")
            self.prompt_get_email_address_1()
            self.current_step = self.step_get_email_address_1
            return

        EMAIL_SENDER.send_email('Test Subject', 'Test Body', ['snagglepants@gmail.com'])
        self.session.disconnect_client()