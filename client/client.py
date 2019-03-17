import requests
import socket

from packagemanager import get_packages


def main():
    hostname = socket.gethostname()
    assert not hostname.startswith("localhost"), "Could not get real hostname"
    assert len(hostname.split('.')) > 1, "Could not get FQDN"

    packages = get_packages()
    requests.post('http://localhost:8000/publish', json={"hostname": hostname, "packages": packages})


if __name__ == '__main__':
    main()
