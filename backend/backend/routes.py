from logging import getLogger
from aiohttp import web
# WALLETS {
from .views import handler_signin, handler_signup, handler_wallet_create, handler_wallet_list
# WALLETS }
# BALANCE {
from .views import handler_generate, handler_address_balance, handler_balance
# BALANCE }


logger = getLogger(__name__)


def setup_routes(app):
    logger.warning('setup routes')

    # WALLETS {
    app.router.add_post('/signup', handler_signup)
    app.router.add_post('/signin', handler_signin)
    app.router.add_get('/wallets', handler_wallet_list)
    app.router.add_post('/wallets', handler_wallet_create)
    # WALLETS }

    # BALANCE {
    app.router.add_get('/wallets/{id}/balance', handler_balance)
    app.router.add_post('/generate', handler_generate)
    app.router.add_post('/balance', handler_address_balance)
    # BALANCE }
