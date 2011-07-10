import boto

import settings

class SESBackend(object):
    """
    This class sends emails through Amazon's Simple Email Service. 
    """
    def send_email(self, subject, body, to_addresses):
        """
        :param str subject: The subject of the email.
        :param str body: The body of the email to send.
        :param list to_addresses: A list of email addresses to send the
            email to.
        """
        conn = boto.connect_ses(settings.AWS_ACCESS_KEY_ID,
                                settings.AWS_SECRET_ACCESS_KEY)

        conn.send_email(settings.SERVER_EMAIL_FROM, subject, body, to_addresses)