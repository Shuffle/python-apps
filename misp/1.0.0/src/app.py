#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import urllib3
import requests

from walkoff_app_sdk.app_base import AppBase

class Misp(AppBase):
    """
    An example of a Walkoff App.
    Inherit from the AppBase class to have Redis, logging, and console logging set up behind the scenes.
    """
    __version__ = "1.0.0"
    app_name = "misp"

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.verify = False
        super().__init__(redis, logger, console_logger)

    async def search(self, apikey, url, data):
        url = "%s/attributes/restSearch" % url
        headers = {
            "Accept": "application/json",
            "Content-type": "application/json",
            "Authorization": apikey,
        }

        return requests.post(url, headers=headers, data=data, verify=self.verify).text
        
if __name__ == "__main__":
    asyncio.run(Misp.run(), debug=True)
