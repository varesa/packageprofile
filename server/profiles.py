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
        cur.execute("TRUNCATE TABLE pp_loading;")

        for chunk in chunks(packages, 100):
            values = ', '.join(
                f"('{pkg['name']}', '{pkg['version']}', '{pkg['release']}', '{pkg['arch']}')" for pkg in chunk
            )
            cur.execute(f"INSERT INTO pp_loading (name, version, release, arch) VALUES {values};")

        cur.execute("""SELECT md5(string_agg(name || version || release || arch, ', ')) FROM pp_loading;""")
        hash = cur.fetchone()[0]
        print(hash)

        cur.execute(f"""SELECT id FROM pp_profile WHERE hash = '{hash}';""")
        existing = cur.fetchone()[0]

        if not existing:
            cur.execute("""
            INSERT INTO pp_package (name)
            SELECT DISTINCT name FROM pp_loading
            ON CONFLICT DO NOTHING;""")

            cur.execute("""
            INSERT INTO pp_package_instance (package, version, release, arch)
            SELECT pp_package.id, version, release, arch FROM pp_loading 
                JOIN pp_package ON pp_package.name = pp_loading.name
            ON CONFLICT DO NOTHING;""")

            cur.execute(f"""
            INSERT INTO pp_profile (hash)
            VALUES ('{hash}')
            RETURNING id;
            """)
            profile_id = cur.fetchone()[0]

            cur.execute(f"""
            INSERT INTO pp_package_link (package_instance, profile)
            SELECT pp_package_instance.id, {profile_id} FROM pp_package_instance
                JOIN pp_loading ON 
                    (pp_package_instance.version = pp_loading.version AND
                    pp_package_instance.release = pp_loading.release AND
                    pp_package_instance.arch = pp_loading.arch);
            """)
        conn.commit()

        return existing if existing else profile_id
