from logging import getLogger, basicConfig

from loader.bus import main
from loader.application import make_app


class App:
    async def __call__(self):
        logger.warning('App()()')
        await main(medium=True)

    pass


basicConfig()
logger = getLogger(__name__)

app = make_app()


if __name__ == '__main__':
    main()
