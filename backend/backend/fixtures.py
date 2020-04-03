from typing import Tuple
from asyncio import gather

from pytest import fixture
from aiohttp.test_utils import TestClient

from backend.application import web, setup_app
from backend.db import init_db


async def clear_db(app):
    await app.db.users.delete_many({})
    await app.db.wallets.delete_many({})


@fixture()
def app(loop, aiohttp_client):
    app = web.Application()

    setup_app(app)

    loop.run_until_complete(init_db(app, testing=True))
    loop.run_until_complete(clear_db(app))

    return app


@fixture()
def client(loop, aiohttp_client, app):
    return loop.run_until_complete(aiohttp_client(app))


@fixture()
async def notsignedin_client(loop, aiohttp_client, app):
    client = loop.run_until_complete(aiohttp_client(app))
    return client


@fixture()
def clients(loop, aiohttp_client, app) -> Tuple[TestClient, TestClient]:
    return loop.run_until_complete(gather(aiohttp_client(app), aiohttp_client(app)))


@fixture()
async def signedin_client(client: TestClient):
    async with client as client:
        await client.post('/signup', json=dict(email='user@site.net', password='password'))

        resp = await client.post('/signin', json=dict(email='user@site.net', password='password'))

        client.session_id = (await resp.json())['session_id']

        yield client
