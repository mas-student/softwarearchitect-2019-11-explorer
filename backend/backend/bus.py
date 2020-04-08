from dataclasses import dataclass
from json import dumps
from typing import Union, Generator
from asyncio import run
from logging import getLogger

import aioredis

from common.bus import (
    connect, publish, subscribe, call,
    Connection, BaseBus
)
from common.logging import debug


logger = getLogger(__name__)


HOSTNAME = 'bus'


@dataclass
class Income:
    connection: Connection
    data: dict
    address: str
    value: float
    balance: float


async def handler_income(app, income: Income):
    logger.warning(f'handling income {income.address} {income.value} {income.balance}')

    oks = 0
    for ws in app.websockets:
        data = dict(address=income.address, value=income.value, balance=income.balance)
        buffer = dumps(data)

        try:
            result = await ws.send_str(buffer)

        except Exception as e:
            logger.warning(f'{type(e)}("{e}") happened when sending to websocket {ws}')

        try:
            await set_balance(income.address, income.balance)

        except Exception as e:
            logger.warning(f'{type(e)}("{e}") happened when setting balance for {income.address}')

        else:
            oks += 1

    logger.warning(f'handled income {income.address} {income.value} with {oks} times')


@dataclass
class Bus(BaseBus):
    async def incomes(self) -> Generator[Income, None, None]:
        async for data in subscribe('incomes', self.hostname):
            async with (await connect(self.hostname)) as testing_connection:
                try:
                    mid = data.get('id')
                    address = data.get('address')
                    value = data.get('value')
                    balance = data.get('balance')

                    yield Income(data=data, connection=testing_connection, address=address, value=value, balance=balance)

                except Exception as e:
                    logger.error(str(e))
                    await publish(testing_connection, {'result': False, 'error': str(e), 'id': mid}, queue_name='testing')
                    import traceback
                    traceback.print_exc()



async def handling_incomes(app):
    bus: Bus = app.bus
    async for income in bus.incomes():
        data = income.data

        mid = data.get('id')

        await handler_income(app, income)

        await publish(income.connection, {'result': True, 'error': None, 'id': mid}, queue_name='testing')


async def set_balance(address: str, value: float = None):
    redis = await aioredis.create_redis_pool(
        'redis://redis'
    )

    if value is None:
        data = await call('commands', 'calc_balance', {'address': address}, receive_from='testing')
        value = data['result']

    await redis.set(address, value)

    redis.close()
    await redis.wait_closed()

    return value


async def get_balance(address: str):
    redis = await aioredis.create_redis_pool(
        'redis://redis'
    )
    value = await redis.get(address, encoding='utf-8')

    redis.close()
    await redis.wait_closed()

    if value is None:
        balance = await set_balance(address, value=None)
    else:
        balance = float(value)

    return balance


async def init_bus(app):
    debug('initiating bus')
    app.bus = Bus(hostname=HOSTNAME)
    debug('initiated bus')


def main(medium=False):
    async def _():
        logger.warning('backend bus connecting')
        from backend.application import make_testing_app
        app = await make_testing_app()

        return await init_bus(app)

    if medium:
        return _()

    else:
        run(_())


if __name__ == '__main__':
    HOSTNAME = 'localhost'
    main()