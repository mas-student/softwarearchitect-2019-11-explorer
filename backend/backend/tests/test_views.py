from operator import itemgetter
from typing import Tuple
from unittest.mock import patch, AsyncMock

from pytest import mark
from aiohttp.test_utils import TestClient

from backend.fixtures import (
    app, client, notsignedin_client, clients, signedin_client
)
from backend.db import User, Wallet


# WALLETS {

async def test_signup(client: TestClient):
    resp = await client.post('/signup', json=dict(email='e', password='password'))

    assert resp.status == 201
    assert 'email' in await resp.json()
    assert (await User.count(client.app.db)) == 1


async def test_signin_ok(client: TestClient):
    await client.post('/signup', json=dict(email='user@site.net', password='password'))

    resp = await client.post('/signin', json=dict(email='user@site.net', password='password'))
    first = await resp.json()

    assert 'session_id' in first, await resp.text()

    second = await resp.json()

    assert first['session_id'] == second['session_id']


async def test_signin_user_not_found(client: TestClient):
    await client.post('/signup', json=dict(email='user@site.net', password='password'))

    resp = await client.post('/signin', json=dict(email='another@site.net', password='password'))

    assert resp.status == 401
    assert 'user not found' in await resp.text()


async def test_signin_incorrect_password(client: TestClient):
    await client.post('/signup', json=dict(email='user@site.net', password='password'))

    resp = await client.post('/signin', json=dict(email='user@site.net', password='nonpassword'))

    assert resp.status == 401
    assert 'password incorrect' in await resp.text()


async def test_wallet_create(client: TestClient):
    async with client as client:
        assert await Wallet.count(client.app.db) == 0

        await client.post('/signup', json=dict(email='user@site.net', password='password'))
        await client.post('/signin', json=dict(email='user@site.net', password='password'))

        resp = await client.post('/wallets', json={'address': 'A1'})

        assert resp.status == 201
        assert await Wallet.count(client.app.db) == 1


async def test_wallet_create_invalid_format(client: TestClient):
    async with client as client:
        assert await Wallet.count(client.app.db) == 0

        await client.post('/signup', json=dict(email='user@site.net', password='password'))
        await client.post('/signin', json=dict(email='user@site.net', password='password'))

        resp = await client.post('/wallets', json={})

        assert resp.status == 400
        assert await Wallet.count(client.app.db) == 0


async def test_wallet_list(signedin_client: TestClient):
    await signedin_client.post('/wallets', json={'address': 'A1'})

    resp = await signedin_client.get('/wallets?session_id')

    assert len((await resp.json())) == 1
    assert 'A1' in set(map(itemgetter('address'), (await resp.json())))


async def test_wallet_list_with_session_id(clients: Tuple[TestClient, TestClient]):
    client, notsignedin_client = clients
    await client.post('/signup', json=dict(email='user@site.net', password='password'))

    resp = await client.post('/signin', json=dict(email='user@site.net', password='password'))

    session_id = (await resp.json())['session_id']

    await client.post('/wallets', json={'address': 'A1'})

    resp = await notsignedin_client.get(f'/wallets?session_id={session_id}')

    data = await resp.json()

    assert resp.status == 200
    assert len((data)) == 1
    assert 'A1' in set(map(itemgetter('address'), (await resp.json())))

# WALLETS }

# BALANCE {

@patch('backend.views.call', AsyncMock(return_value={'result': -1}))
async def test_handler_wallet_balance(client: TestClient):
    async with client as client:
        await client.post('/signup', json=dict(email='user@site.net', password='password'))
        await client.post('/signin', json=dict(email='user@site.net', password='password'))
        await client.post('/wallets', json={'address': 'A1'})

        resp = await client.get('/wallets')

        data = await resp.json()

        assert isinstance(data, list)

        id, *_ = map(itemgetter('id'), data)

        resp = await client.get(f'/wallets/{id}/balance')

        balance = itemgetter('balance')(await resp.json())

        assert balance == -1


@patch('backend.views.call', AsyncMock(return_value={'result': 'address1'}))
async def test_handler_generate(client: TestClient):
    async with client as client:
        resp = await client.post('/generate', json=dict(address='address1'))

        address = itemgetter('address')(await resp.json())

        assert address == 'address1'

# BALANCE }

# SEARCH {

@mark.skip('later')
async def test_search(client: TestClient):
    async with client as client:
        resp = await client.get('/search?q=123')

# SEARCH }

async def test_db(app):
    assert app.db is not None
