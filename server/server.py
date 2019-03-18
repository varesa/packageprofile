from flask import Flask, request, jsonify

from database import init_db
from profiles import create_profile, set_host_profile
from profiles import get_host_profile, get_profile_packages, get_packages


app = Flask(__name__)


@app.route('/publish', methods=['POST'])
def publish():
    hostname = request.json['hostname']
    packages = request.json['packages']

    profile = create_profile(packages)
    set_host_profile(hostname, profile)

    return "OK"


@app.route('/query', methods=['GET'])
def query():
    if 'host' in request.args.keys():
        host = request.args.get('host')
        profile = get_host_profile(host)
        packages = get_profile_packages(profile)

        if 'format' in request.args.keys() and request.args.get('format') == 'plain':
            return ''.join(f"{p[0]}.{p[1]}-{p[2]}.{p[3]}\n" for p in packages)
        else:
            return jsonify(packages)

    if 'packages' in request.args.keys():
        filter = request.args.get('packages')
        packages = get_packages(filter)

        if 'format' in request.args.keys() and request.args.get('format') == 'plain':
            return ''.join(f"{p[0]}: {p[1]}.{p[2]}-{p[3]}.{p[4]}\n" for p in packages)
        else:
            return "not implemented"

    return "?"


def main():
    init_db()
    app.run(host="0.0.0.0", port=8000)


if __name__ == '__main__':
    main()
