"""
This module contains stuff that is done on the game's first startup.
"""

from twisted.internet.defer import inlineCallbacks
from src.utils import logger

@inlineCallbacks
def setup_db(conn):
    """
    Setup our Postgres database. Do some really basic population.
    """

    yield conn.runOperation(
        """
        CREATE TABLE dott_objects
        (
          id serial NOT NULL,
          name character varying NOT NULL,
          parent character varying NOT NULL,
          location_id integer,
          base_type character varying(10) NOT NULL,
          originally_controlled_by_account_id integer,
          controlled_by_account_id integer,
          description character varying,
          data json,
          CONSTRAINT dott_objects_id PRIMARY KEY (id),
          CONSTRAINT dott_objects_location_id_to_id FOREIGN KEY (location_id)
            REFERENCES dott_objects (id) MATCH SIMPLE
            ON UPDATE NO ACTION ON DELETE NO ACTION,
          CONSTRAINT dott_objects_controlled_by_account_id_to_id FOREIGN KEY (controlled_by_account_id)
            REFERENCES dott_accounts (id) MATCH SIMPLE
            ON UPDATE NO ACTION ON DELETE NO ACTION,
          CONSTRAINT dott_objects_originally_controlled_by_account_id_to_id FOREIGN KEY (originally_controlled_by_account_id)
            REFERENCES dott_accounts (id) MATCH SIMPLE
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        WITH (
          OIDS=FALSE
        );
        """
    )

    logger.info("dott_objects table created.")