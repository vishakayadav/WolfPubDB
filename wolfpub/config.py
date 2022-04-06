"""
Contains configurations, Each module will pick configuration from here.
"""

from configparser import ConfigParser
import os
from ast import literal_eval
from dotenv import load_dotenv

load_dotenv()

CONFIG_PARSER = ConfigParser(os.environ)
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.conf')
CONFIG_PARSER.readfp(open(CONFIG_FILE))

BASE_DIR = os.getcwd()

API_SETTINGS = literal_eval(CONFIG_PARSER.get("WolfPubAPI", "api_settings"))
RESTPLUS_SETTINGS = literal_eval(CONFIG_PARSER.get("WolfPubAPI", 'restplus_settings'))
MARIADB_SETTINGS = literal_eval(CONFIG_PARSER.get("WolfPubAPI", 'mariadb_settings'))
