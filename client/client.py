import configparser
import requests
import socket

from packagemanager import get_packages


def main():
    hostname = socket.gethostname()
    assert not hostname.startswith("localhost"), "Could not get real hostname"
    assert len(hostname.split('.')) > 1, "Could not get FQDN"

    config = configparser.ConfigParser()
    config.read("/etc/packageprofile.conf")
    url = config['server']['url']
    print("URL: {}".format(url))

    packages = get_packages()
    r = requests.post(url, json={"hostname": hostname, "packages": packages})
    print("Result: HTTP {}".format(r.status_code))


if __name__ == '__main__':
    main()
