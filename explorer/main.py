from logging import getLogger, basicConfig

from aiohttp import web

from explorer.application import make_app


basicConfig()
logger = getLogger(__name__)


if __name__ == '__main__':
    app = make_app()
    web.run_app(app)
