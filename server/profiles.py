import itertools
from typing import Generator, Collection

from database import conn, get_cursor

def chunks(i: Collection, n: int) -> Generator:
    """
    Split the iterable into chunks of n or less elements
    :param i: iterable to split
    :param n: maximum size of a chunk
    :return: chunks
    """
    return (i[x:x+n] for x in range(0, len(i), n))


def create_profile(packages: dict):
    with get_cursor() as cur:
        cur.execute("INSERT INTO pp_session DEFAULT VALUES RETURNING session");

        session = str(cur.fetchone()[0])
        table = "pp_temp_" + ("00" + session)[-3:]

        cur.execute(f"""
        CREATE TEMPORARY TABLE {table} (
            id serial PRIMARY KEY,
            name text NOT NULL,
            version text NOT NULL, 
            release text NOT NULL, 
            arch text NOT NULL
        );
        """)

        for chunk in chunks(packages, 1000):
            values_q = ', '.join(f"(%s, %s, %s, %s)" for pkg in chunk)
            values_v = list(itertools.chain.from_iterable([(pkg['name'], pkg['version'], pkg['release'], pkg['arch']) for pkg in chunk]))

            cur.execute(f"INSERT INTO {table} (name, version, release, arch) VALUES {values_q};", values_v)

        cur.execute(f"""
        SELECT 
            md5(string_agg(
                name || '/' || version || '/' || release || '/' || arch, 
                ', ' ORDER BY (name, version, release, arch)
            )) 
        FROM {table};
        """)
        hash = cur.fetchone()[0]

        cur.execute(f"""SELECT id FROM pp_profile WHERE hash = '{hash}';""")

        existing = cur.fetchone()

        if not existing:
            cur.execute(f"""
            INSERT INTO pp_package (name)
            SELECT DISTINCT name FROM {table}
            ON CONFLICT DO NOTHING;
            """)

            cur.execute(f"""
            INSERT INTO pp_package_instance (package, version, release, arch)
            SELECT pp_package.id, version, release, arch FROM {table} 
                JOIN pp_package ON pp_package.name = {table}.name
            ON CONFLICT DO NOTHING;
            """)

            cur.execute(f"""
            INSERT INTO pp_profile (hash)
            VALUES ('{hash}')
            RETURNING id;
            """)
            profile_id = cur.fetchone()[0]

            cur.execute(f"""
            INSERT INTO pp_package_link (package_instance, profile)
            SELECT pp_package_instance.id, {profile_id} FROM pp_package_instance
                JOIN {table} ON (
                    pp_package_instance.version = {table}.version AND
                    pp_package_instance.release = {table}.release AND
                    pp_package_instance.arch = {table}.arch)
                JOIN pp_package ON (
                    pp_package.name = {table}.name AND
                    pp_package.id = pp_package_instance.package);
            """)

        cur.execute(f"""
        DROP TABLE {table};
        DELETE FROM pp_session WHERE session = {session};""")

        conn.commit()

        return existing[0] if existing else profile_id


def set_host_profile(host, new_profile):
    with get_cursor() as cur:
        cur.execute(f"INSERT INTO pp_host (name) VALUES (%s) ON CONFLICT DO NOTHING;", (host,))

        cur.execute(f"""
        SELECT pp_profile_link.profile FROM pp_profile_link 
        JOIN pp_host ON pp_profile_link.host = pp_host.id 
        WHERE pp_host.name = %s
        ORDER BY pp_profile_link.id DESC LIMIT 1;
        """, (host,))
        result = cur.fetchone()

        if result:
            old_profile = result[0]
            if new_profile == old_profile:
                return

        cur.execute(f"""
        INSERT INTO pp_profile_link (host, profile, date)
        SELECT pp_host.id, %s, now() FROM pp_host
        WHERE pp_host.name = %s;
        """, (new_profile, host))
        conn.commit()


def get_host_profile(host):
    with get_cursor() as cur:
        cur.execute(f"""
        SELECT profile FROM pp_profile_link 
        WHERE host = (SELECT id FROM pp_host WHERE name = %s) ORDER BY id DESC LIMIT 1;
        """, (host,))
        return cur.fetchone()[0]


def get_profile_packages(profile):
    with get_cursor() as cur:
        cur.execute(f"""
        SELECT pp_package.name, pp_package_instance.version, pp_package_instance.release, pp_package_instance.arch 
        FROM pp_package_link JOIN pp_package_instance ON pp_package_link.package_instance = pp_package_instance.id 
        JOIN pp_package ON pp_package_instance.package = pp_package.id 
        WHERE profile = %s;
        """, (profile,))
        return cur.fetchall()


def get_packages(query):
    with get_cursor() as cur:
        cur.execute(f"""
        SELECT pp_host.name, pp_package.name, 
               pp_package_instance.version, pp_package_instance.release, pp_package_instance.arch
        FROM pp_package 
        JOIN pp_package_instance ON pp_package.id = pp_package_instance.package 
        JOIN pp_package_link ON pp_package_link.package_instance = pp_package_instance.id 
        JOIN pp_profile_link ON pp_package_link.profile = pp_profile_link.profile 
        JOIN pp_host ON pp_host.id = pp_profile_link.host 
        WHERE pp_package.name LIKE %s AND 
              pp_profile_link.id IN (SELECT max(id) FROM pp_profile_link GROUP BY host);
        """, (query,))
        return cur.fetchall()
