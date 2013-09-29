"""
Some assorted DB-related utils.
"""

import psycopg2
import psycopg2.extras
from txpostgres import txpostgres

import settings


class txPGDictConnection(txpostgres.Connection):
    """
    This is a txpostgres Connection sub-class that returns rows as dicts,
    instead of tuples.

    .. note:: This does incur some additional overhead, and is going to be
        slower than the default cursor. This is not a problem for us most
        of the time, since we only really use the DB for persistence.
    """

    @staticmethod
    def dict_connect(*args, **kwargs):
        kwargs['connection_factory'] = psycopg2.extras.DictConnection
        conn = psycopg2.connect(*args, **kwargs)
        return conn

    # Overriding the default connection factory.
    connectionFactory = dict_connect


def get_db_connection_kwargs(db_mode='production', include_db=True):
    """
    :param str db_mode: Either 'test' or 'production'.
    :param bool include_db: If False, exclude the database name.
    :returns: A dict of connection params to pass to psycopg2 for the
        given mode (test or production). Excludes None and values that
        evaluate to boolean False.
    """

    if db_mode == 'production':
        conn_info = settings.DATABASE.copy()
    else:
        conn_info = settings.TEST_DATABASE.copy()

    if not conn_info['user']:
        del conn_info['user']

    if not conn_info['port']:
        del conn_info['port']

    if not include_db:
        del conn_info['database']

    return conn_info