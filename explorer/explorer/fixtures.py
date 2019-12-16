from pytest import fixture

from explorer.application import web, setup_app
from explorer.db import init_db


async def clear_db(app):
    await app.db.users.delete_many({})
    await app.db.wallets.delete_many({})


@fixture()
def app(loop, aiohttp_client):
    app = web.Application()

    setup_app(app)

    loop.run_until_complete(init_db(app))
    loop.run_until_complete(clear_db(app))

    return app


@fixture()
def client(loop, aiohttp_client, app):
    return loop.run_until_complete(aiohttp_client(app))
