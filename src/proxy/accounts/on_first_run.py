"""
This module contains stuff that is done on the game's first startup.
"""

from twisted.internet.defer import inlineCallbacks
import settings
from src.utils import logger


@inlineCallbacks
def setup_db(conn):
    """
    Setup our Postgres database. Do some really basic population.

    :param AccountStore store:

    """

    yield conn.runOperation(
        """
        CREATE TABLE dott_accounts
        (
          id serial NOT NULL,
          username character varying(30) NOT NULL,
          currently_controlling_id integer,
          email character varying(50) NOT NULL,
          password character varying(255) NOT NULL,
          CONSTRAINT dott_accounts_id PRIMARY KEY (id),
          CONSTRAINT dott_accounts_currently_controlling_id FOREIGN KEY (currently_controlling_id)
              REFERENCES dott_objects (id) MATCH SIMPLE
              ON UPDATE NO ACTION ON DELETE NO ACTION,
          CONSTRAINT dott_accounts_username UNIQUE (username)
        )
        WITH (
          OIDS=FALSE
        );
        CREATE INDEX fki_dott_accounts_currently_controlling_id
          ON dott_accounts
          USING btree
          (currently_controlling_id);
        """
    )

    logger.info("%s table created." % settings.ACCOUNT_TABLE_NAME)