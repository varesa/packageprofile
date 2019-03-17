from flask import Flask, request

from database import init_db
from profiles import create_profile, set_host_profile

app = Flask(__name__)


@app.route('/publish', methods=['POST'])
def publish():
    hostname = request.json['hostname']
    packages = request.json['packages']

    profile = create_profile(packages)
    set_host_profile(hostname, profile)

    return "OK"


def main():
    init_db()
    app.run(host="0.0.0.0", port=8000)


if __name__ == '__main__':
    main()
