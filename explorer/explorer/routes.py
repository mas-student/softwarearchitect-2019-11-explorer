from .views import signin, signup, wallet_create, wallet_list

def setup_routes(app):
    app.router.add_post('/singup', signup)
    app.router.add_post('/singin', signin)
    app.router.add_get('/wallets', wallet_list)
    app.router.add_post('/wallets', wallet_create)
