import boto

import settings

class OutboundEmail(object):
    """
    This class sends emails through Amazon's Simple Email Service. 
    """
    def __init__(self, subject, body, to_addresses):
        """
        :param str subject: The subject of the email.
        :param str body: The body of the email to send.
        :param list to_addresses: A list of email addresses to send the
            email to.
        """
        self.subject = subject
        self.body = body
        self.to_addresses = to_addresses

    def send_email(self):
        """
        Sends the email via SES.
        """
        conn = boto.connect_ses(
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY
        )

        conn.send_email(
            settings.SERVER_EMAIL_FROM,
            self.subject,
            self.body,
            self.to_addresses
        )