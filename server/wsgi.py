
# gunicorn wants to find 'application' to run
from server import app
from database import init_db

init_db()


def application(environ, start_response):
    return app(environ, start_response)
