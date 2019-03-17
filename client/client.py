import configparser
import requests
import socket

from packagemanager import get_packages


CONFIG_LOCATION = "/etc/packageprofile.conf"
FALLBACK_URL = "http://localhost:8000/publish"


def main():
    hostname = socket.gethostname()
    assert not hostname.startswith("localhost"), "Could not get real hostname"
    assert len(hostname.split('.')) > 1, "Could not get FQDN"

    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_LOCATION)
        url = config['server']['url']
        print("URL: {}".format(url))
    except KeyError:
        print("No config file found at " + CONFIG_LOCATION + ", falling back to " + FALLBACK_URL)
        url = FALLBACK_URL

    packages = get_packages()
    r = requests.post(url, json={"hostname": hostname, "packages": packages})
    print("Result: HTTP {}".format(r.status_code))


if __name__ == '__main__':
    main()
