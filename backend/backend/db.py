from logging import getLogger
from dataclasses import dataclass
from typing import (
    List, Optional,
    TypeVar, Type,
)

from bson.objectid import ObjectId
import motor.motor_asyncio

from common.logging import debug


'''
DAO module
'''

logger = getLogger(__name__)


@dataclass
class ModelMixin:
    T = TypeVar('T', bound='Base')

    COLLECTION = None

    _id: ObjectId

    @classmethod
    async def create(cls, db, **data) -> 'ModelMixin':
        result = await db[cls.COLLECTION].insert_one(data)
        return cls( **data)

    @classmethod
    async def get(cls, db, **query) -> Optional['ModelMixin']:
        data = await db[cls.COLLECTION].find_one(query)

        if data is None:
            return

        return cls(**data)

    @classmethod
    async def update(cls, db, query: dict, **values) -> Optional['ModelMixin']:
        await db[cls.COLLECTION].update_one(query, {'$set': values})

        data = await db[cls.COLLECTION].find_one(query)

        if data is None:
            return

        return cls(**data)

    @classmethod
    async def filter(cls: Type[T], db, **query) -> T:
        return [cls(**data) async for data in db[cls.COLLECTION].find(query)]

    @classmethod
    async def all(cls, db) -> List['ModelMixin']:
        return [cls(**data) async for data in db[cls.COLLECTION].find()]

    @classmethod
    async def count(cls, db) -> int:
        return await db[cls.COLLECTION].count_documents({})


@dataclass
class User(ModelMixin):
    COLLECTION = 'users'

    email: str
    password: str


@dataclass
class Wallet(ModelMixin):
    COLLECTION = 'wallets'

    user: str
    address: str


async def init_db(app, testing=False):
    debug('initiating db')

    host = 'localhost' if testing else 'db'

    client = motor.motor_asyncio.AsyncIOMotorClient(host, 57017 if testing else 27017)
    app.db = client.testing_backend if testing else client.backend

    debug('initiated db')
