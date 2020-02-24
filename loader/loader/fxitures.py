from pytest import fixture
from loader.corenode import Corenode


@fixture
async def corenode():
    return Corenode(None)