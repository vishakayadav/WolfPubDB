import logging
import os

from flask import url_for
from flask_restplus import Api, apidoc

from wolfpub import config

log = logging.getLogger(__name__)


class CustomApi(Api):
    def __init__(self, *args, **kwargs):
        super(CustomApi, self).__init__(*args, **kwargs)

    @property
    def specs_url(self):
        return config.API_SETTINGS["DOMAIN_NAME"] + config.API_SETTINGS["URL_PREFIX"] + "/swagger.json"


api = CustomApi(version=config.API_SETTINGS.get('VERSION'), title=config.API_SETTINGS.get('TITLE'),
                description="API for Wolf Pub")

custom_apidoc = apidoc.Apidoc('restplus_custom_doc', __name__, template_folder='templates',
                              static_folder=os.path.dirname(apidoc.__file__) + '/static', static_url_path='/swaggerui')


@custom_apidoc.add_app_template_global
def swagger_static(filename):
    return url_for('restplus_custom_doc.static', filename='bower/swagger-ui/dist/{0}'.format(filename))
