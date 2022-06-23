import socket
import time
import random
import json
import markdownify

from walkoff_app_sdk.app_base import AppBase


class Markdownify(AppBase):
    __version__ = "1.0.0"
    app_name = "Markdownify"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    def html_to_markdown(self, some_string):
        return markdownify.markdownify(some_string, heading_style="ATX")

if __name__ == "__main__":
    Markdownify.run()

