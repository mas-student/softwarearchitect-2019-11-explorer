from dataclasses import dataclass
from logging import getLogger
from asyncio import get_event_loop, sleep
from time import monotonic
from typing import Union, Optional
from json import dumps, loads

from aio_pika import connect as aio_pika_connect, Channel, Queue, Connection, Message


logger = getLogger(__name__)


BUS_URI=''


@dataclass
class BaseBus:
    hostname: str


@dataclass
class ResponsibleMessage:
    name: str
    params: dict
    return_address: str
    connection: Connection
    mid: Optional[int]

    async def respond(self, result, error=None):
        logger.warning(f'responding {result}')
        await publish(self.connection, {'result': result, 'error': error, 'id': self.mid}, queue_name=self.return_address)
        logger.warning(f'responded {result}')



async def connect(hostname='bus', wait_for=30.0) -> Connection:
    logger.warning(f'connecting to bus on {hostname} waiting for {wait_for}')
    loop = get_event_loop()

    started_at = monotonic()
    while True:
        try:
            connection = await aio_pika_connect(f"amqp://guest:guest@{hostname}/", loop=loop)

        except Exception as e:
            logger.warning(f'elapsed {monotonic() - started_at} {e}')

            await sleep(0.25)

            if monotonic() - started_at > wait_for:
                raise e

        else:
            break

    logger.warning('connected')

    return connection


async def make_queue(connection: Connection, queue_name: str, timeout=None):
    channel: Channel = await connection.channel()
    queue: Queue = await channel.declare_queue(queue_name, auto_delete=True, timeout=timeout)
    return queue


async def publish(connection: Connection, message: Union[str, dict], queue_name):
    logger.warning(f'publishing {message} into {queue_name}')

    routing_key = queue_name
    channel = await connection.channel()
    await channel.default_exchange.publish(
        Message(
            body=(dumps(message) if type(message) is dict else message).encode('utf-8'),
        ),
        routing_key=routing_key,
        timeout=3.0,
    )

    logger.warning('published')


async def receive(connection: Connection, queue_name: str, wait_for=5.0) -> Optional[bytes]:
    logger.warning(f'receiving from {queue_name}')
    queue = await make_queue(connection, queue_name, timeout=3.0)

    data = None
    started_at = monotonic()
    while True:
        try:
            message = await queue.get(timeout=3.0)

        except Exception as e:
            if monotonic() - started_at > wait_for:
                logger.error(f'{type(e)}{e} raises while receiving from {queue_name}')
                break

            await sleep(0.25)

        else:
            logger.warning(f'received {message} for {monotonic() - started_at} seconds')
            async with message.process():
                data = loads(message.body.decode())
                break

    return data


async def exhaust(queue_name: str):
    message = True
    async with (await connect()) as connection:
        while message:
            message = await receive(connection, queue_name)


async def call(quene_name, command_name, params, receive_from='returns'):
    await exhaust(receive_from)

    async with (await connect()) as testing_connection:
        async with (await connect()) as connection:
            await publish(connection, {
                "name": command_name,
                "params": params,
                "id": 1,
                "return_address": receive_from
            }, quene_name)
        return await receive(testing_connection, receive_from)


async def subscribe(queue_name, hostname):
    logger.warning(f'subscribing to {queue_name}')
    async with (await connect(hostname=hostname)) as connection:
        queue = await make_queue(connection, queue_name)
        async with queue.iterator() as queue_iter:
            logger.warning(f'receiving from "{queue_name}"')
            async for message in queue_iter:
                logger.warning(f'received {message.body} from {queue_name}')
                try:
                    async with message.process():
                        data = loads(message.body)
                        yield data

                except Exception as e:
                    logger.error(f'{type(e)}{e} raises while subscribing to {queue_name} ')
                    continue
