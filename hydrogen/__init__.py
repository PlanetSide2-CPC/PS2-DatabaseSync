"""The program initializes the configuration file and executes the main program."""
import json
import logging

logger = logging.getLogger(__name__)

with open("hydrogen/config/config.json", mode="r", encoding="utf8") as config:
    __config__ = json.load(config)
