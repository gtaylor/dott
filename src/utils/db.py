"""
Some assorted DB-related utils.
"""

import psycopg2
import psycopg2.extras
from txpostgres import txpostgres


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
        return psycopg2.connect(*args, **kwargs)

    # Overriding the default connection factory.
    connectionFactory = dict_connect