import logging
import psycopg2
import psycopg2.extensions

import database_schema

conn = psycopg2.connect("postgresql://postgres@localhost/postgres")

# Test query:
# SELECT format('%s-%s-%s.%s', pp_package.name, pp_package_instance.version, pp_package_instance.release, pp_package_instance.arch) FROM pp_package JOIN pp_package_instance ON pp_package.id=pp_package_instance.package;


class LoggingCursor(psycopg2.extensions.cursor):
    def execute(self, sql, args=None):
        logger = logging.getLogger('sql_debug')
        logger.error(self.mogrify(sql, args))

        try:
            psycopg2.extensions.cursor.execute(self, sql, args)
        except Exception as exc:
            logger.error("%s: %s" % (exc.__class__.__name__, exc))
            raise


def init_db():
    cur = conn.cursor(cursor_factory=LoggingCursor)
    database_schema.update_schema(cur)
    conn.commit()
    cur.close()


def add_package_instance(package):
    cur = conn.cursor(cursor_factory=LoggingCursor)

    cur.execute(f"""
    INSERT INTO pp_package 
        (name) VALUES ('{package['name']}')
        ON CONFLICT (name) DO NOTHING;
    """)

    cur.execute(f"SELECT id FROM pp_package WHERE name = '{package['name']}';")
    package_id = cur.fetchone()[0]

    cur.execute(f"""
    INSERT INTO pp_package_instance
        (package, version, release, arch) VALUES 
        ({package_id}, '{package['version']}', '{package['release']}', '{package['arch']}');
    """)

    conn.commit()
    cur.close()


def get_package_instances(package=None):
    cur = conn.cursor(cursor_factory=LoggingCursor)

    filter = ""
    if package:
        filter = f" WHERE pp_package.name = '{package}'"

    cur.execute(f"""
    SELECT pp_package.name, pp_package_instance.version, pp_package_instance.release, pp_package_instance.arch 
    FROM pp_package 
    JOIN pp_package_instance ON pp_package.id=pp_package_instance.package
    {filter};
    """)

    packages = [{"name": r[0], "version": r[1], "release": r[2], "arch": r[3]} for r in cur.fetchall()]
    cur.close()

    return packages
