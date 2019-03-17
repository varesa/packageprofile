import logging

logger = logging.getLogger(__name__)


def create_initial(cur):
    logger.info("Creating version table")
    cur.execute("CREATE TABLE pp_version (version integer PRIMARY KEY);")
    cur.execute("INSERT INTO pp_version (version) VALUES (0);")


def upgrade_version1(cur):
    cur.execute("""
    CREATE TABLE pp_package (
        id serial PRIMARY KEY, 
        name text UNIQUE NOT NULL
    );
    
    CREATE TABLE pp_package_instance (
        id serial PRIMARY KEY, 
        package integer NOT NULL REFERENCES pp_package(id), 
        version text NOT NULL, 
        release text NOT NULL, 
        arch text NOT NULL,
        UNIQUE(package, version, release, arch)
    );
    
    CREATE TABLE pp_profile (
        id serial PRIMARY KEY,
        hash text UNIQUE NOT NULL
    );
    
    CREATE TABLE pp_package_link (
        id serial PRIMARY KEY,
        package_instance integer NOT NULL REFERENCES pp_package_instance(id),
        profile integer NOT NULL REFERENCES pp_profile(id)
    );
    
    CREATE TABLE pp_host (
        id serial PRIMARY KEY,
        name text UNIQUE NOT NULL
    );
    
    CREATE TABLE pp_profile_link (
        id serial PRIMARY KEY,
        host integer NOT NULL REFERENCES pp_host(id),
        profile integer NOT NULL REFERENCES pp_profile(id),
        date timestamp NOT NULL
    );
    
    CREATE TABLE pp_loading (
        id serial PRIMARY KEY,
        name text NOT NULL,
        version text NOT NULL, 
        release text NOT NULL, 
        arch text NOT NULL
    );
    
    UPDATE pp_version SET version = 1;
    """)


def upgrade_version2(cur):
    cur.execute("""
    DROP TABLE pp_loading;
    
    CREATE TABLE pp_session (
        session serial PRIMARY KEY
    );
    
    UPDATE pp_version SET version = 2;
    """)


def update_schema(cur):
    cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pp_version')")
    tables_exist = cur.fetchone()[0]

    if not tables_exist:
        create_initial(cur)

    cur.execute("SELECT version FROM pp_version;")
    version = cur.fetchone()[0]

    if version < 1:
        logger.info("Upgrading to version 1")
        upgrade_version1(cur)

    if version < 2:
        logger.info("Upgrading to version 2")
        upgrade_version2(cur)
