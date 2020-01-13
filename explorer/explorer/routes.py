from .views import signin, signup, wallet_create, wallet_list

def setup_routes(app):
    app.router.add_post('/signup', signup)
    app.router.add_post('/signin', signin)
    app.router.add_get('/wallets', wallet_list)
    app.router.add_post('/wallets', wallet_create)
