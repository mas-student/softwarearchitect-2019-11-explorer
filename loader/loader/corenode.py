from asyncio import run, sleep, gather, Event, wait_for, CancelledError
from typing import Optional, Generator
from dataclasses import dataclass

from aiohttp import ClientSession, BasicAuth
from json import dumps
from pprint import pprint

from logging import getLogger

from loader.models import Block


logger = getLogger(__name__)


URL = 'http://bitcoin-server:18443/'
NODE_USERNAME='u'
NODE_PASSWORD='p'


class Corenode:
    def __init__(self, url=Optional[str]):
        self.url = url or URL

        self.generating = Event()

    async def execute_call(self, method, *params):
        signature = f'{method} ({", ".join(map(str, params))})'
        async with ClientSession(auth=BasicAuth(NODE_USERNAME, NODE_PASSWORD)) as session:
            async with session.post(self.url, data=dumps(dict(method=method, params=params))) as response:
                try:
                    data = await response.json()
                except Exception as e:
                    text = await response.text()
                    logger.warning(f'{type(e).__name__}:{e} () raises when executing {signature}\n{text}')
                    return
                logger.warning(f'{signature} -> {data}')
                return data['result']

    @dataclass
    class Iterator:
        corenode: 'Corenode'
        available: int = -1
        necessary = None

        def __aiter__(self):
            return self

        async def __anext__(self) -> Optional[Block]:
            result = None
            while result is None:
                self.necessary = await self.corenode.execute_call('getblockcount') or 0 - 1

                if self.available < self.necessary:
                    self.available += 1
                    block_data = await self.corenode.execute_call(
                        'getblock',
                        await self.corenode.execute_call(
                            'getblockhash',
                            self.available),
                        2
                    )
                    result = Block.from_dict(block_data)

                else:
                    logger.warning(f'before waiting for {self.corenode.generating}')
                    try:
                        await wait_for(self.corenode.generating.wait(), timeout=3.0)
                    except Exception as e:
                        logger.warning(f'{type(e).__name__}{e} raises while waiting for {self.corenode.generating}')
                        continue
                    logger.warning(f'after waiting for {self.corenode.generating}')
                    self.corenode.generating.clear()

            return result

    def iterator(self):
        return self.Iterator(corenode=self)

    async def generate(self, address=None):
        logger.warning(f'generating {address}')
        if address is None:
            address = await self.execute_call('getnewaddress')
            logger.warning(f'call getnewaddress -> {address}')
        result = await self.execute_call('generatetoaddress', 101, address)
        logger.warning(f'call generatetoaddress -> {result}')
        result = await self.execute_call('getblockcount')
        logger.warning(f'call getblockcount -> {result}')
        result = await self.execute_call('getbalance')
        logger.warning(f'call getbalance -> {result}')

        self.generating.set()

        return address

    async def print_blocks(self):
        async for block in self.iterator():
            pprint(block.height)

    async def iterate(self) -> Generator[Block, None, None]:
        async for block in self.iterator():
            yield block

    async def blocks(self) -> Generator[Block, None, None]:
        async for block in self.iterator():
            yield block


async def init_node(app, url=None):
    app.node = Corenode(url=url if url else URL)

    return app


def main():
    from loader.application import Application
    app = Application()

    async def _():
        await init_node(app)
        await gather(app.node.print_blocks(), app.node.generate())

    run(_())


if __name__ == '__main__':
    URL = 'http://localhost:18443/'
    main()