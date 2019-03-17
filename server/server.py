from database import init_db, add_package_instance, get_package_instances


def main():
    init_db()
    add_package_instance({
        "name": "testpkg",
        "version": "1.0.0",
        "release": "1.el0",
        "arch": "noarch"
    })
    add_package_instance({
        "name": "testpkg",
        "version": "1.0.0",
        "release": "2.el0",
        "arch": "noarch"
    })
    add_package_instance({
        "name": "other-pkg",
        "version": "2.1.0",
        "release": "1.el0",
        "arch": "x86_64"
    })
    print(get_package_instances())



if __name__ == '__main__':
    main()
