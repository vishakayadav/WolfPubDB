"""
Module for Handling the Configuration for execution Data Gaps Job
"""
import copy
import itertools
import json
import traceback
from operator import itemgetter

import requests

from wolfpub import config
from wolfpub.api.utils.custom_exceptions import *
from wolfpub.api.utils.logger import WOLFPUB_LOGGER as logger


class DistributorHandler(object):
    """
    Focuses on providing functionality over Data Gaps Job Configuration
    """

    def __init__(self, db):
        self.db = db