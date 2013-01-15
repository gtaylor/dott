"""
Assorted validators for things like usernames and email addresses.
"""
import re

def is_email_valid(email_address, max_length=90):
    """
    Given an email address, returns ``True`` if it appears to be valid. This
    makes no attempt to verify that it does exist, only that it appears to
    be well-formed.

    :rtype: bool
    :returns: ``True`` if email address appears to be valid, ``False`` if not.
    """
    email_re = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$',
        re.IGNORECASE)
    
    if email_re.match(email_address):
        return len(email_address) <= max_length
    else:
        return False

def is_username_valid(username, min_length=2, max_length=25):
    """
    Given a username, returns ``True`` if it is valid, ``False`` if not.

    :rtype: bool
    :returns: ``True`` for valid usernames, ``False`` otherwise.
    """
    username_re = re.compile(r"^[\w_ ]+$")

    if username_re.match(username):
        return min_length <= len(username) <= max_length
    else:
        return False