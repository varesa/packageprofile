import logging
import os
import psycopg2
import psycopg2.extensions

import database_schema

try:
    conn: psycopg2.extensions.connection = psycopg2.connect(os.environ['POSTGRESQL_URL'])
except KeyError:
    assert False, "Please set the environment variable POSTGRESQL_URL to a valid connection string"

global queries
queries = 0


class LoggingCursor(psycopg2.extensions.cursor):
    def execute(self, sql, args=None):
        logger = logging.getLogger('sql_debug')
        logger.error(self.mogrify(sql, args))
        global queries
        queries += 1
        logger.error(f"Queries executed: {queries}")

        try:
            psycopg2.extensions.cursor.execute(self, sql, args)
        except Exception as exc:
            logger.error("%s: %s" % (exc.__class__.__name__, exc))
            raise


def get_cursor() -> psycopg2.extensions.cursor:
    return conn.cursor(cursor_factory=LoggingCursor)


def init_db():
    with get_cursor() as cur:
        database_schema.update_schema(cur)
        conn.commit()
