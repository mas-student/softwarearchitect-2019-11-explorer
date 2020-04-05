from logging import getLogger
from asyncio import create_task, gather

from cryptography import fernet
import base64
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp import web

from common.logging import debug
from .routes import setup_routes
from .db import init_db
from .bus import init_bus, handling_incomes

logger = getLogger(__name__)


def setup_app(app):
    app.websockets = []
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    session_setup(app, EncryptedCookieStorage(secret_key))
    setup_routes(app)

    return app


async def start_background_tasks(app):
    app['handling_incomes'] = create_task(handling_incomes(app))


async def cleanup_background_tasks(app):
    app['handling_incomes'].cancel()
    await gather(app['handling_incomes'])


async def on_ready(app):
    logger.warning('Backend is ready')


def make_app():
    app = web.Application()

    setup_app(app)
    
    app.on_startup.append(init_db)
    app.on_startup.append(init_bus)

    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)

    app.on_startup.append(on_ready)

    return app


async def make_testing_app():
    app = web.Application()

    setup_app(app)

    await init_db(app, False)

    return app


def main():
    debug(f'{__name__}, {main}')
    app = make_app()
    web.run_app(app, host='0.0.0.0', port=8080)