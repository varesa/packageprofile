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


def get_package_instances(package=None):
    with get_cursor() as cur:

        filter = ""
        if package:
            filter = f" WHERE pp_package.name = '{package['name']}'"
            for field in ('version', 'release', 'arch'):
                if field in package.keys():
                    filter += f" AND pp_package_instance.{field} = '{package[field]}'"

        cur.execute(f"""
        SELECT pp_package.id, pp_package_instance.id, 
            pp_package.name, pp_package_instance.version, pp_package_instance.release, pp_package_instance.arch 
        FROM pp_package 
        JOIN pp_package_instance ON pp_package.id=pp_package_instance.package
        {filter};
        """)

        packages = [{"packge_id": r[0], "instance_id": r[1],
                     "name": r[2], "version": r[3], "release": r[4], "arch": r[5]}
                    for r in cur.fetchall()]

        return packages
