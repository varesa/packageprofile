import logging
import psycopg2
import psycopg2.extensions

import database_schema

conn: psycopg2.extensions.connection = psycopg2.connect("postgresql://postgres@localhost/postgres")

# Test query:
# SELECT format('%s-%s-%s.%s', pp_package.name, pp_package_instance.version, pp_package_instance.release, pp_package_instance.arch) FROM pp_package JOIN pp_package_instance ON pp_package.id=pp_package_instance.package;

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
    cur = conn.cursor(cursor_factory=LoggingCursor)
    database_schema.update_schema(cur)
    conn.commit()
    cur.close()


def add_package_instance(package: dict) -> int:
    """
    Add a new package and a package instance to the database if they do not already exist,
    returning the id of the instance
    :param package: dict with the keys 'name', 'version', 'release' and 'arch'
    :return: id of the pp_package_instance row
    """
    with get_cursor() as cur:

        #
        # Select an existing or create a new package
        #
        cur.execute(f"SELECT id FROM pp_package WHERE name = '{package['name']}';")
        result = cur.fetchone()

        if result:
            package_id = result[0]
        else:
            cur.execute(f"""
            INSERT INTO pp_package 
                (name) VALUES ('{package['name']}')
                RETURNING id;
            """)
            package_id = cur.fetchone()[0]

        #
        # Select an existing or create a new package instance
        #
        cur.execute(f"SELECT id FROM pp_package_instance"
                    f" WHERE package = {package_id} "
                    f"    AND version = '{package['version']}' "
                    f"    AND release = '{package['release']}' "
                    f"    AND arch = '{package['arch']}';")
        result = cur.fetchone()
        if result:
            instance_id = result[0]
        else:
            cur.execute(f"""
            INSERT INTO pp_package_instance 
                (package, version, release, arch) 
            VALUES 
                ({package_id}, '{package['version']}', '{package['release']}', '{package['arch']}')
            RETURNING id;
            """)
            instance_id = cur.fetchone()[0]

        conn.commit()
        return instance_id


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
