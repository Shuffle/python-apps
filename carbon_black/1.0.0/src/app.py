#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import time
import random
import cbapi
import requests
import urllib3

from walkoff_app_sdk.app_base import AppBase

class CarbonBlack(AppBase):
    """
    Carbon Black integration for WALKOFF with some basic features
    """
    __version__ = "1.0.0"
    app_name = "carbon_black"

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        self.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        super().__init__(redis, logger, console_logger)

    async def isolate(self, url, token, hostname):
        cb = cbapi.CbResponseAPI(url=url, token=token, ssl_verify=self.verify)
        isolated = False
        
        for sensor in cb.select(cbapi.response.Sensor).where("hostname:%s" % hostname):
            sensor.network_isolation_enabled = True
            sensor.save()
            isolated = True

        if isolated:
            return True
        
        return False 

    async def process_search(self, url, token, query):
        cb = cbapi.CbResponseAPI(url=url, token=token, ssl_verify=self.verify)
        
        search = cb.select(cbapi.response.Process).where(query)
        return len(search)

    async def binary_search(self, url, token, query):
        cb = cbapi.CbResponseAPI(url=url, token=token, ssl_verify=self.verify)
        
        search = cb.select(cbapi.response.Binary).where(query)
        return len(search)

if __name__ == "__main__":
    asyncio.run(CarbonBlack.run(), debug=True)
