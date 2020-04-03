from dataclasses import dataclass
from json import dumps
from typing import Union, Generator

from asyncio import run
from logging import getLogger

from common.bus import (
    connect, publish, subscribe,
    Connection, BaseBus
)


logger = getLogger(__name__)


HOSTNAME = 'bus'


@dataclass
class Income:
    connection: Connection
    data: dict
    address: str
    value: float


async def handler_income(app, income: Income):
    logger.warning(f'handling income {income.address} {income.value}')
    oks = 0
    for ws in app.websockets:
        data = dict(address=income.address, value=income.value)
        buffer = dumps(data)
        try:
            result = await ws.send_str(buffer)
        except Exception as e:
            logger.warning(f'{type(e)}("{e}") happened when sending to websocket {ws}')

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

                    yield Income(data=data, connection=testing_connection, address=address, value=value)

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


async def init_bus(app):
    logger.warning('init bus')
    app.bus = Bus(hostname=HOSTNAME)


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