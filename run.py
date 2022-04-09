from flask import Blueprint
from gevent import pywsgi

from wolfpub import app
from wolfpub import config
from wolfpub.api.restplus import api, custom_apidoc


def configure_app(flask_app):
    """
    To set Swagger Configuration
    """
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = config.RESTPLUS_SETTINGS["RESTPLUS_SWAGGER_UI_DOC_EXPANSION"]
    flask_app.config['RESTPLUS_VALIDATE'] = config.RESTPLUS_SETTINGS["RESTPLUS_VALIDATE"]
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = config.RESTPLUS_SETTINGS["RESTPLUS_MASK_SWAGGER"]
    flask_app.config['ERROR_404_HELP'] = config.RESTPLUS_SETTINGS["RESTPLUS_ERROR_404_HELP"]
    flask_app.config['SWAGGER'] = {"swagger_version": "2.0", "openapi": "3.0.0"}


def initialize_app(flask_app):
    '''
        TODO:
            -> Move namespaces import here
            -> Run mongo in fg to see number of connections
    '''
    configure_app(flask_app)
    blueprint = Blueprint('api', __name__, url_prefix=config.API_SETTINGS["URL_PREFIX"])
    api.init_app(blueprint)

    from wolfpub.api.controllers.distributor import ns as distributor_ns
    api.add_namespace(distributor_ns)

    from wolfpub.api.controllers.content_writers import ns as content_writers_ns
    api.add_namespace(content_writers_ns)

    from wolfpub.api.controllers.report import ns as report_ns
    api.add_namespace(report_ns)

    from wolfpub.api.controllers.healthcheck import ns as healthcheck_namespace
    api.add_namespace(healthcheck_namespace)

    # consider replacing with namespace
    flask_app.register_blueprint(custom_apidoc, url_prefix=config.API_SETTINGS["URL_PREFIX"] + "/static")
    flask_app.register_blueprint(blueprint)


if __name__ == '__main__':
    initialize_app(app)
    app.run(host=config.API_SETTINGS['HOST'],
            port=int(config.API_SETTINGS['PORT']),
            debug=bool(config.API_SETTINGS['FLASK_DEBUG']))
    # WSGI_SERVER = pywsgi.WSGIServer((config.API_SETTINGS["HOST"], int(config.API_SETTINGS["PORT"])), app)
    # WSGI_SERVER.serve_forever()
