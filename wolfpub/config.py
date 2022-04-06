"""
Contains configurations, Each module will pick configuration from here.
"""

from configparser import ConfigParser
import os
from ast import literal_eval
from dotenv import load_dotenv

load_dotenv()
# dot_env_path = os.getenv("ENV_PATH", None)
# if dot_env_path is not None:
#     load_dotenv(dotenv_path=dot_env_path, verbose=True)
# else:
#     raise Exception("No environment file provided.")

CONFIG_PARSER = ConfigParser(os.environ)
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.conf')
CONFIG_PARSER.readfp(open(CONFIG_FILE))

BASE_DIR = os.getcwd()

API_SETTINGS = literal_eval(CONFIG_PARSER.get("WolfPubAPI", "api_settings"))
RESTPLUS_SETTINGS = literal_eval(CONFIG_PARSER.get("WolfPubAPI", 'restplus_settings'))
MARIADB_SETTINGS = literal_eval(CONFIG_PARSER.get("WolfPubAPI", 'mariadb_settings'))
