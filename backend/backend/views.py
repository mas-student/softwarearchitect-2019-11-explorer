from logging import getLogger

from aiohttp_session import get_session
from aiohttp import web
from aiohttp.web_request import Request


logger = getLogger(__name__)


# WALLETS {

from .db import User, Wallet

# WALLETS }

# BALANCE {

from common.bus import call

# BALANCE }


async def handler_signup(request: Request):
    user = await User.create(
        request.app.db,
        email=(await request.json())['email'],
        password=(await request.json())['password'],
    )

    return web.json_response(dict(id=str(user._id), email=user.email), status=201)


async def handler_signin(request):
    session = await get_session(request)

    email = (await request.json())['email']
    password = (await request.json())['password']

    user = await User.get(request.app.db, email=email)

    if not user:
        return web.Response(status=401, body='user not found')

    if user.password != password:
        return web.Response(status=401, body='password incorrect')

    session['email'] = user.email

    return web.Response(body='ok')


async def handler_wallet_create(request):
    data = await request.json()

    if 'address' not in data:
        return web.Response(status=400, body='invalid wallet data')

    address = data['address']

    session = await get_session(request)
    email = session.get('email')

    db = request.app.db
    user = await User.get(db, email=email)

    data = {'user': user._id, 'address': address}
    wallet = await Wallet.create(db, **data)

    return web.json_response(dict(id=str(wallet._id), address=wallet.address), status=201)


async def handler_wallet_list(request):
    db = request.app.db
    session = await get_session(request)

    email = session.get('email')

    if not email:
        return web.json_response([], status=401)

    user = await User.get(db, email=email)

    wallets = await Wallet.filter(request.app.db, user=user._id)

    data = [dict(id=str(ins._id), address=ins.address) for ins in wallets]

    return web.json_response(data)


async def handler_balance(request):
    db = request.app.db

    id = request.match_info['id']

    from bson.objectid import ObjectId

    wallet = await Wallet.get(db, _id=ObjectId(id))  # TO DO by str

    # TO DO testing -> returns
    data = await call('commands', 'calc_balance', {'address': wallet.address}, receive_from='testing')

    data = {'balance': data['result']}

    return web.json_response(data)


async def handler_address_balance(request):
    logger.warning(f'handling {request} {await request.text()}')
    import json
    try:
        data = await request.json()
    except json.decoder.JSONDecodeError:
        data = {}

    address = data.get('address')

    # TO DO testing -> returns
    data = await call('commands', 'calc_balance', {'address': address}, receive_from='testing')

    data = {'balance': data['result']}

    return web.json_response(data)


async def handler_generate(request):
    logger.warning(f'handling {request} {await request.text()}')
    import json
    try:
        data = await request.json()
    except json.decoder.JSONDecodeError:
        data = {}

    address = data.get('address')

    data = await call('commands', 'generate', {'address': address})

    data = {'address': data['result']}

    return web.json_response(data)
