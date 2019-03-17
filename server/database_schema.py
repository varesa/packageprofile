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


def update_schema(cur):
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
