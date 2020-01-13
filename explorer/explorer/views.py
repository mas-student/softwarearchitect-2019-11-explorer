from aiohttp_session import get_session
from aiohttp import web

from .db import User, Wallet


async def signup(request):
    user = await User.create(
        request.app.db,
        email=(await request.json())['email'],
        password=(await request.json())['password'],
    )

    return web.json_response(dict(id=str(user._id), email=user.email), status=201)


async def signin(request):
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


async def wallet_create(request):
    data = await request.json()

    if 'address' not in data:
        return web.Response(status=400, body='password incorrect')

    address = data['address']

    session = await get_session(request)
    email = session.get('email')

    db = request.app.db
    user = await User.get(db, email=email)

    data = {'user': user._id, 'address': address}
    wallet = await Wallet.create(db, **data)

    return web.json_response(dict(id=str(wallet._id), address=wallet.address), status=201)


async def wallet_list(request):
    db = request.app.db
    session = await get_session(request)

    email = session.get('email')

    if not email:
        return web.json_response([], status=401)

    user = await User.get(db, email=email)

    wallets = await Wallet.filter(request.app.db, user=user._id)

    data = [dict(id=str(ins._id), address=ins.address) for ins in wallets]

    return web.json_response(data)
