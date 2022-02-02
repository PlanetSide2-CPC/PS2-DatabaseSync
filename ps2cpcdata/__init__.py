"""The program initializes the configuration file and executes the main program."""
import json
import logging

logger = logging.getLogger(__name__)

with open("ps2cpcdata/config/config.json", "r") as config:
    __config__ = json.load(config)
