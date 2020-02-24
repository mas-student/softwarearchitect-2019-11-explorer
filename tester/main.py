from logging import getLogger
from unittest.mock import ANY

from pytest import main
from common.bus import call


logger = getLogger(__name__)


async def test_backend():
    assert (
            await call('incomes', 'process', {"address": "address1", "amount": 3.14}, receive_from='testing')
            ==
            {"result": True, "error": None, "id": 1}
    )


async def test_loader():
    assert (
            await call('commands', 'calc_balance', {'address': 'address1'}, receive_from='testing')
            ==
            {"result": 0, "error": None, "id": 1}
    )


async def test_loader_generate():
    assert (
        await call('commands', 'generate', {}, receive_from='testing')
        ==
        {"result": ANY, "error": None, "id": 1}
    )


if __name__ == '__main__':
    main()
