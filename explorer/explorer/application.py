from logging import getLogger

from cryptography import fernet
import base64
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp import web

from .routes import setup_routes
from .db import init_db


logger = getLogger(__name__)


def setup_app(app):
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    session_setup(app, EncryptedCookieStorage(secret_key))
    setup_routes(app)

    return app


def make_app():
    app = web.Application()

    app.on_startup.append(init_db)
    setup_app(app)

    return app
