from logging import getLogger
from typing import Optional
from asyncio import create_task, gather

from pytest import fixture
from aiohttp import web

from loader.commands import handler_commands
from loader.db import init_db, handler_blocks
from loader.bus import Bus, init_bus
from loader.db import DB
from loader.corenode import Corenode, init_node


logger = getLogger(__name__)


class Application():
    db: Optional[DB] = None
    node: Optional[Corenode] = None
    bus: Optional[Bus] = None
    bus_hostname: Optional[str] = None
    pass


async def init_events(app):
    async def on_income(data: dict):
        await app.bus.publish(data, queue_name='incomes')

    app.db.on_income = on_income


async def start_background_tasks(app):
    app['handler_commands'] = create_task(handler_commands(app))
    app['handler_blocks'] = create_task(handler_blocks(app))


async def cleanup_background_tasks(app):
    app['handler_blocks'].cancel()
    app['handler_commands'].cancel()
    await gather(app['handler_blocks'], app['handler_commands'])


async def on_ready(app):
    logger.warning('Loader is ready')


def make_app():
    app = web.Application()

    app.on_startup.append(init_bus)
    app.on_startup.append(init_db)
    app.on_startup.append(init_node)
    app.on_startup.append(init_events)

    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)

    app.on_startup.append(on_ready)

    return app


def main(app=None):
    if app is None:
        app = make_app()
    web.run_app(app)