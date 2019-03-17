import logging
import psycopg2
import psycopg2.extensions

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


def create_initial(cur):
    print("Creating version table")
    cur.execute("CREATE TABLE pp_version (version integer PRIMARY KEY);")
    cur.execute("INSERT INTO pp_version (version) VALUES (0);")


def upgrade_version1(cur):
    cur.execute("""
    CREATE TABLE pp_package (
        id serial PRIMARY KEY, 
        name text UNIQUE
    );""")

    cur.execute("""
    CREATE TABLE pp_package_instance (
        id serial PRIMARY KEY, 
        package integer REFERENCES pp_package(id), 
        version text, 
        release text, 
        arch text
    );""")

    cur.execute("UPDATE pp_version SET version = 1;")


def upgrade_version2(cur):
    cur.execute("""
    CREATE TABLE pp_profile (
        id serial PRIMARY KEY,
        hash text
    );""")

    cur.execute("""
    CREATE TABLE pp_package_link (
        id serial PRIMARY KEY,
        package_instance integer REFERENCES pp_package_instance(id),
        profile integer REFERENCES pp_profile(id)
    );""")

    cur.execute("""
    CREATE TABLE pp_host (
        id serial PRIMARY KEY,
        name text UNIQUE,
        profile integer REFERENCES pp_profile(id)
    );""")

    cur.execute("UPDATE pp_version SET version = 2;")


def init_db():
    cur = conn.cursor(cursor_factory=LoggingCursor)
    cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pp_version')")
    tables_exist = cur.fetchone()[0]

    if not tables_exist:
        create_initial(cur)

    cur.execute("SELECT version FROM pp_version;")
    version = cur.fetchone()[0]

    if version < 1:
        print("Upgrading to version 1")
        upgrade_version1(cur)

    if version < 2:
        print("Upgrading to version 2")
        upgrade_version2(cur)

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
