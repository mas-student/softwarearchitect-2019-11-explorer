from dataclasses import dataclass
from logging import getLogger
from typing import Generator
from asyncio import run

from common.logging import debug
from common.bus import (
    connect, subscribe, BaseBus, publish
)
from loader.commands import Command


logger = getLogger(__name__)


HOSTNAME = 'bus'


@dataclass
class Bus(BaseBus):
    async def publish(self, data: dict, queue_name: str):
        async with (await connect(hostname=self.hostname)) as connection:
            await publish(connection=connection, message=data, queue_name=queue_name)

    async def receiving_commands(self) -> Generator[Command, None, None]:
        async for data in subscribe('commands', hostname=self.hostname):
            async with (await connect(hostname=self.hostname)) as return_connection:
                debug(f'receiving_command {data}')

                if not data.get('return_address'):
                    logger.error('return address is not defined')
                    raise GeneratorExit()

                yield Command(
                    name=data.get('name'),
                    params=data.get('params', {}),
                    mid=data.get('id'),
                    return_address=data.get('return_address'),
                    connection=return_connection
                )


async def init_bus(app):
    app.bus = Bus(hostname=HOSTNAME)


def main(medium=False):
    from loader.application import Application
    from loader.commands import handler_commands
    app = Application()

    async def _():
        await init_bus(app)
        await handler_commands(app)

    return _() if medium else run(_())


if __name__ == '__main__':
    HOSTNAME = 'localhost'
    URL = 'http://localhost:18443/'
    main()
