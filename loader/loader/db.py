from logging import getLogger
from dataclasses import asdict
from json import loads, dumps
from typing import Type, Optional

from plyvel import DB as BaseDB

from loader.models import BlockchainElement, Block, Transaction


logger = getLogger(__name__)


NODE = 'http://bitcoin-server:18443/'


class DB:
    def __init__(self, db_path: str = None):
        self.on_income = lambda data: logger.warning(f'on income {data}')
        if db_path is None:
            db_path = '/tmp/tempdb/'

        self.base = BaseDB(db_path, create_if_missing=True)

    def get_element(self, *args, **kwargs) -> Optional[BlockchainElement]:
        return get_element(self.base, *args, **kwargs)

    def put_element(self, *args, **kwargs):
        put_element(self.base, *args, **kwargs)

    async def put_block(self, block: Block):
        await put_block(self.base, block, self.on_income)

    def get_balance(self, address: str):
        return get_balance(self.base, address)


def get_element(leveldb: BaseDB, key: str, cls: Type[BlockchainElement]) -> Optional[BlockchainElement]:
    # TO DO Generic method
    logger.warning(f'get_element({leveldb}, {key}, {cls})')
    data = loads(leveldb.get(key.encode('utf-8'), b'{}') or b'{}')

    if not data:
        return

    return cls.from_dict(data)


def put_element(leveldb: BaseDB, key: str, element: BlockchainElement):
    data = asdict(element)

    leveldb.put(key.encode('utf-8'), dumps(data).encode('utf-8'))


async def put_block(leveldb: BaseDB, block: Block, on_income):
    leveldb.put(block.hash.encode('utf-8'), dumps(asdict(block)).encode('utf-8'))

    for tx in block.tx:
        put_element(leveldb, tx.txid, tx)
        nos = {}
        for no, vin in enumerate(tx.vin):
            if not vin.txid:
                logger.warning(f'{vin}')
                continue
            input_tx = get_element(leveldb, vin.txid, Transaction)
            if not input_tx:
                continue
            for no, vout in enumerate(input_tx.vout):
                for address in vout.scriptPubKey.addresses:
                    nos.setdefault(address, [None, None])[0] = no
        for no, vout in enumerate(tx.vout):
            for address in vout.scriptPubKey.addresses:
                await on_income(dict(address=address, value=vout.value))
                nos.setdefault(address, [None, None])[1] = no

        for address, (vin, vout) in nos.items():
            address_value = loads(leveldb.get(address.encode('utf-8'), b'[]'))
            address_value.append([block.hash, tx.txid, vin, vout])
            leveldb.put(address.encode('utf-8'), dumps(address_value).encode('utf-8'))


def get_balance(leveldb: Optional[BaseDB], address: str):
    logger.warning(f'getting balance {address}')
    if leveldb is None:
        leveldb = connect()
    result = 0.0
    address_value = loads(leveldb.get(address.encode('utf-8'), b'[]'))
    for block_hash, txid, vin, vout in address_value:
        income = 0.0
        outcome = 0.0
        tx = get_element(leveldb, txid, Transaction)
        if vin is not None:
            outcome = tx.vout[vin].value
        if vout is not None:
            income = tx.vout[vout].value
        logger.warning(f'-{outcome} {txid}')
        logger.warning(f'+{income}  {txid}')
        result += income
        result -= outcome

    logger.warning(f'got balance {address} -> {result}')
    return result


def connect(db_path: Optional[str] = None):
    if db_path is None:
        db_path = '/tmp/tempdb/'

    return DB(db_path, create_if_missing=True)


async def init_db(app):
    app.db = DB()


async def handler_blocks(app):
    logger.warning('handling blocks')
    async for block in app.node.blocks():
        logger.warning(f'handling block {block}')
        await app.db.put_block(block)


def main(medium=False):
    from asyncio import run
    from loader.application import Application
    from loader.corenode import init_node
    app = Application()

    async def _():
        await init_db(app)
        await init_node(app, NODE)
        await handler_blocks(app)

    return _() if medium else run(_())


if __name__ == '__main__':
    NODE = 'http://localhost:18443/'
    main()

