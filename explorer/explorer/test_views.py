from operator import itemgetter

from aiohttp.test_utils import TestClient

from explorer.fixtures import app, client
from explorer.db import User, Wallet


async def test_signup(client: TestClient):
    resp = await client.post('/singup', data=dict(email='e', password='password'))

    assert resp.status == 201
    assert 'email' in await resp.json()
    assert (await User.count(client.app.db)) == 1


async def test_signin_ok(client: TestClient):
    await client.post('/singup', data=dict(email='user@site.net', password='password'))

    resp = await client.post('/singin', data=dict(email='user@site.net', password='password'))
    text = await resp.text()

    assert 'ok' in text


async def test_signin_user_not_found(client: TestClient):
    await client.post('/singup', data=dict(email='user@site.net', password='password'))

    resp = await client.post('/singin', data=dict(email='another@site.net', password='password'))

    assert resp.status == 401
    assert 'user not found' in await resp.text()


async def test_signin_incorrect_password(client: TestClient):
    await client.post('/singup', data=dict(email='user@site.net', password='password'))

    resp = await client.post('/singin', data=dict(email='user@site.net', password='nonpassword'))

    assert resp.status == 401
    assert 'password incorrect' in await resp.text()


async def test_wallet_create(client: TestClient):
    async with client as client:
        assert await Wallet.count(client.app.db) == 0

        await client.post('/singup', data=dict(email='user@site.net', password='password'))
        await client.post('/singin', data=dict(email='user@site.net', password='password'))

        resp = await client.post('/wallets', data={'address': 'A1'})

        assert resp.status == 201
        assert await Wallet.count(client.app.db) == 1


async def test_wallet_list(client: TestClient):
    async with client as client:
        await client.post('/singup', data=dict(email='user@site.net', password='password'))

        resp = await client.get('/wallets')

        assert resp.status == 401
        assert len(await resp.json()) == 0

        await client.post('/singin', data=dict(email='user@site.net', password='password'))
        await client.post('/wallets', data={'address': 'A1'})

        resp = await client.get('/wallets')

        assert len((await resp.json())) == 1
        assert 'A1' in set(map(itemgetter('address'), (await resp.json())))


async def test_db(app):
    assert app.db is not None
