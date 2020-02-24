from dataclasses import asdict, replace
from json import loads
from operator import itemgetter
from unittest.mock import patch

from chardet import jpcntx
from pytest import fixture

from loader.db import put_block, get_balance
from loader.models import Block, Transaction, Output

try:
    from asyncmock import AsyncMock
except NameError:
    from unittest.mock import AsyncMock

import plyvel


@fixture
def block() -> Block:
    return Block.dummy()

@fixture
def leveldb():
    db = plyvel.DB('/tmp/testdb/', create_if_missing=True)

    keys = [*map(itemgetter(0), db.iterator())]

    for key in keys:
        db.delete(key)

    yield db

    db.close()


from plyvel import DB

def test_leveldb(leveldb: DB):
    assert leveldb.closed == False

    leveldb.put(b'key', b'value')

    assert leveldb.get(b'key') == b'value'

    assert leveldb.get(b'another-key', b'default-value') == b'default-value'

    leveldb.delete(b'key')

    assert leveldb.get(b'key', b'default-value') == b'default-value'

    leveldb.close()

    assert leveldb.closed == True


def test_put_block(leveldb, block: Block):
    put_block(leveldb, block)

    assert loads(leveldb.get(block.hash.encode('utf-8'), b'{}')) == asdict(block)

    assert loads(leveldb.get(block.tx[0].txid.encode('utf-8'), b'{}')) == asdict(block.tx[0])

    address_key = block.tx[0].vout[0].scriptPubKey.addresses[0].encode('utf-8')
    address_value = [[block.hash, block.tx[0].txid, None, 0]]

    assert loads(leveldb.get(address_key, b'{}')) == address_value


def test_get_balance(leveldb):
    block1 = Block.dummy()
    block2 = Block.dummy()

    block1.tx[0].vin = []
    put_block(leveldb, block1)

    block2.hash = 'block2'
    block2.tx[0].txid = 'tx2'
    block2.tx[0].vin[0].txid = 'tx1'
    block2.tx[0].vout[0].scriptPubKey.addresses[0] = 'address2'
    block2.tx[0].vout.append(Output.dummy())
    block2.tx[0].vout[1].value = 0.5
    block2.tx[0].vout[1].scriptPubKey.addresses[0] = 'address1'
    put_block(leveldb, block2)

    balance = get_balance(leveldb, block1.tx[0].vout[0].scriptPubKey.addresses[0])

    assert balance == 0.5
