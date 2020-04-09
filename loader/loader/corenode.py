from logging import getLogger
from asyncio import run, sleep, gather, Event, wait_for, CancelledError, TimeoutError
from typing import Optional, Generator
from dataclasses import dataclass

from aiohttp import ClientSession, BasicAuth
from json import dumps
from pprint import pprint

from common.logging import debug
from loader.models import Block


logger = getLogger(__name__)


URL = 'http://bitcoin-server:18443/'
NODE_USERNAME='u'
NODE_PASSWORD='p'


class Corenode:
    def __init__(self, url=Optional[str]):
        self.block_count = 0
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
                debug(f'{signature} -> {data}')
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
                    debug(f'before waiting for {self.corenode.generating}')

                    waited = False

                    try:
                        await wait_for(self.corenode.generating.wait(), timeout=3.0)
                    except (TimeoutError, CancelledError):
                        pass
                    except Exception as e:
                        logger.warning(f'{type(e).__name__}{e} raises while waiting for {self.corenode.generating}')
                        continue

                    else:
                        waited = True

                    debug(f'{"Success" if waited  else "Failure"} after waiting for {self.corenode.generating}')

                    self.corenode.generating.clear()

            return result

    def iterator(self, start:int=0):
        return self.Iterator(corenode=self, available=start-1)

    async def generate(self, address=None):
        debug(f'generating {address}')
        if address is None:
            address = await self.execute_call('getnewaddress')
            debug(f'call getnewaddress -> {address}')
        result = await self.execute_call('generatetoaddress', 101, address)
        debug(f'call generatetoaddress -> {result}')
        result = await self.execute_call('getblockcount')
        debug(f'call getblockcount -> {result}')
        result = await self.execute_call('getbalance')
        debug(f'call getbalance -> {result}')

        self.generating.set()

        return address

    async def print_blocks(self):
        async for block in self.iterator():
            pprint(block.height)

    async def iterate(self) -> Generator[Block, None, None]:
        async for block in self.iterator():
            yield block

    async def blocks(self, start: int) -> Generator[Block, None, None]:
        # TO DP SAVE LATEST
        # RENAMED INTO ITERATE BLOCKS
        self.block_count = 0
        async for block in self.iterator(start):
            self.block_count += 1
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