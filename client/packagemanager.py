try:
    import dnf
    package_manager = "dnf"
except ImportError:
    import yum
    package_manager = "yum"


def package_to_dict(package):
    return {
        "name": package.name,
        "version": package.version,
        "release": package.release,
        "arch": package.arch,
    }


def get_dnf_packages():
    packages = []
    base = dnf.base.Base()
    base.fill_sack(load_system_repo=True, load_available_repos=False)
    for package in base.sack.query().installed():
        packages.append(package_to_dict(package))
    return packages


def get_yum_packages():
    packages = []
    base = yum.YumBase()
    for package in base.rpmdb.returnPackages():
        packages.append(package_to_dict(package))
    return packages


def get_packages():
    if package_manager == "dnf":
        return get_dnf_packages()
    else:
        return get_yum_packages()
