from typing import List, Optional

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass
class ElasticSearchMixin:
    ES_INDEX = None

    @property
    def es_id(self) -> str:
        return ''


@dataclass_json
@dataclass
class Income:
    address: str
    amount: float


@dataclass
class Address:
    value: str

    @property
    def es_id(self) -> str:
        return self.value


@dataclass_json
@dataclass
class BlockchainElement:
    pass


@dataclass_json
@dataclass
class Input(BlockchainElement):
    txid: Optional[str] = None
    vout: Optional[int] = None

    @classmethod
    def dummy(cls):
        return Input(txid='tx1', vout=0)


@dataclass_json
@dataclass
class ScriptPubKey(BlockchainElement):
    addresses: Optional[List[str]] = field(default_factory=list)

    @classmethod
    def dummy(cls):
        return ScriptPubKey(addresses=['address1'])


@dataclass_json
@dataclass
class Output(BlockchainElement):
    value: float
    scriptPubKey: ScriptPubKey

    @classmethod
    def dummy(cls):
        return Output(value=1, scriptPubKey=ScriptPubKey.dummy())


@dataclass_json
@dataclass
class Transaction(BlockchainElement, ElasticSearchMixin):
    ES_INDEX = 'transaction'
    txid: str
    vin: List[Input]
    vout: List[Output]

    @property
    def es_id(self) -> str:
        return self.txid

    @classmethod
    def dummy(cls):
        return Transaction(txid='tx1', vin=[Input.dummy()], vout=[Output.dummy()])


@dataclass_json
@dataclass
class Block(BlockchainElement):
    ES_INDEX = 'block'

    height: int
    hash: str
    nTx: int
    confirmations: int
    tx: List[Transaction] = field(repr=False)

    @property
    def es_id(self) -> str:
        return self.txid

    @classmethod
    def dummy(cls):
        # TO DO cls(
        return Block(
            height=1,
            hash='block1',
            nTx=1,
            confirmations=1,
            tx=[Transaction.dummy()]
        )

    @property
    def addresses(self):
        return {
            address
            for tx in self.tx
            for vout in tx.vout
            for address in vout.scriptPubKey.addresses or []
        }

    def get_incomes(self, subscriptions: List[str]):
        return {
            (address, vout.value)
            for tx in self.tx
            for vout in tx.vout
            for address in vout.scriptPubKey.addresses or []
            if address in subscriptions
        }

    @property
    def incomes(self):
        return [
            Income(address=address, amount=vout.value)
            for tx in self.tx
            for vout in tx.vout
            for address in vout.scriptPubKey.addresses or []
        ]