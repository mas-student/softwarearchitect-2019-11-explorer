from unittest.mock import patch

try:
    from asyncmock import AsyncMock
except NameError:
    from unittest.mock import AsyncMock

from backend.bus import main


def test_smoke():
    subscribe_mocked = AsyncMock()
    with patch('backend.bus.subscribe', subscribe_mocked):
        main(None)

    assert subscribe_mocked.called