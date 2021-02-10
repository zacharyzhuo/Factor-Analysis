from flask import Flask, app
from flask_restful import Api

# local packages
from api import routes

# default mongodb configuration
default_config = {
    'MONGODB_SETTINGS': {
        'host': 'localhost',
        'port': 27017,
        'username': 'admin',
        'password': 'password',
        'authentication_source': 'admin'
        },
    'JSON_AS_ASCII': False
    }


# param: dict; return: app
def get_flask_app(config: dict = None) -> app.Flask:
    """
    Initializes Flask app with given configuration.
    Main entry point for wsgi (gunicorn) server.
    :param config: Configuration dictionary
    :return: app
    """
    # init flask
    flask_app = Flask(__name__)
    # configure app
    config = default_config if config is None else config
    flask_app.config.update(config)

    # init api and routes
    api = Api(app=flask_app)
    routes.create_routes(api=api)

    return flask_app


if __name__ == '__main__':
    # Main entry point when run in stand-alone mode.
    app = get_flask_app()
    app.run(debug=True, host="0.0.0.0", port=8090)
    # app.run(debug=True)
    