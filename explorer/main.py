from logging import getLogger, basicConfig

from aiohttp import web
from explorer.application import make_app


basicConfig()
logger = getLogger(__name__)

app = make_app()

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8080)
