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


import traceback


def debug(f):
    def wrapper(*args, **kwargs):
        try:
            logger.warning(f'{f.__name__} being called with {args} {kwargs}')
            ret = f(*args, **kwargs)
            logger.warning(f'{f.__name__} called with {args} {kwargs}')
        except Exception as e:
            logger.error(f'{type(e).__name__}({str(e)}) when {f.__name__} called with {args} {kwargs}')
            traceback.print_tb()
            raise

        return ret

    return wrapper


async def get_email(request: Request):
    session = await get_session(request)

    session_id = int(request.rel_url.query.get('session_id') or '0')

    session = await get_session(request)

    emails = session.get('emails', {})

    request.app.sessions = getattr(request.app, 'sessions', {})

    if not session_id:
        return session.get('email')

    elif session_id and request.app.sessions.get(session_id):
        return request.app.sessions[session_id].get('email')

    else:
        raise Exception('unknown session id')


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

    session['id'] = session.get('id', id(session))
    session['email'] = user.email
    request.app.sessions = getattr(request.app, 'sessions', {})
    request.app.sessions[session['id']] = dict(email=session['email'])

    return web.json_response(dict(session_id=session['id'], email=user.email), status=200)


async def handler_wallet_create(request):
    data = await request.json()

    if 'address' not in data:
        return web.Response(status=400, body='invalid wallet data')

    try:
        email = await get_email(request)

    except Exception as e:
        return web.Response(status=400, body=str(e))

    address = data['address']

    db = request.app.db
    user = await User.get(db, email=email)

    wallet = await Wallet.get(request.app.db, address=address)
    if wallet:
        return web.json_response(dict(id=str(wallet._id), address=wallet.address), status=200)

    data = {'user': user._id, 'address': address}
    wallet = await Wallet.create(db, **data)

    return web.json_response(dict(id=str(wallet._id), address=wallet.address), status=201)


async def get_balance(address: str):
    # TO DO testing -> returns
    data = await call('commands', 'calc_balance', {'address': address}, receive_from='testing')

    return data['result']


async def handler_wallet_list(request: Request):
    db = request.app.db

    try:
        email = await get_email(request)

    except Exception as e:
        return web.Response(status=400, body=str(e))

    if email == 'admin@site.net':
        wallets = await Wallet.all(request.app.db)

    elif email:
        user = await User.get(db, email=email)

        if not user:
            wallets = []

        else:
            wallets = await Wallet.filter(request.app.db, user=user._id)

    else:
         return web.json_response([], status=401)

    data = [
        dict(id=str(ins._id), address=ins.address, balance=await get_balance(ins.address))
        for ins in wallets
    ]

    return web.json_response(data)


async def handler_wallet_balance(request):
    db = request.app.db

    id = request.match_info['id']

    from bson.objectid import ObjectId

    wallet = await Wallet.get(db, _id=ObjectId(id))  # TO DO by str

    data = await get_balance(wallet.address)

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


async def websocket_handler(request):
    import aiohttp

    ws = web.WebSocketResponse()

    app = request.app

    app.websockets.append(ws)

    await ws.prepare(request)

    logger.warning(f'websocket connection inited {len(app.websockets)-1}')

    async for msg in ws:
        logger.warning(f'MSG {msg}')
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str('42')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error(f'ws connection closed with exception {ws.exception()}')

    app.websockets.remove(ws)

    logger.warning('websocket connection closed')

    return ws
