################################
#	Flask
################################

from app.app import create_app

app = create_app(production=False)
app.run(
    host=app.config['APP_HOST'],
    port=app.config['APP_PORT'],
    debug=app.config['APP_DEBUG_FLASK'],
    ssl_context=app.config['APP_SSL_CONTEXT']
)
