from logging import getLogger
from dataclasses import dataclass

from common.logging import debug
from common.bus import (
    ResponsibleMessage
)


logger = getLogger(__name__)


@dataclass
class Command(ResponsibleMessage):
    pass


async def handler_commands(app):
    debug(f'handling commands')
    try:
        async for command in app.bus.receiving_commands():
            debug(f'handling command {command}')

            if command.name == 'generate':
                address = command.params.get('address')
                address = await app.node.generate(address=address)
                await command.respond(address)

            elif command.name == 'calc_balance':
                address = command.params.get('address')
                balance = app.db.get_balance(address)
                await command.respond(balance)

            else:
                error = f'unknown command {command.name}'
                await command.respond(None, error)

            debug(f'handled command {command}')

    except Exception as e:
        logger.error(f'{type(e).__name__}:{e} raises while handling commands')