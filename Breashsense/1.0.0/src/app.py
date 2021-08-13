import socket
import asyncio
import time
import random
import json
import requests

from walkoff_app_sdk.app_base import AppBase

class BreachSense(AppBase):
    __version__ = "1.0.0"
    app_name = "Breachsense"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    async def run_query(self, api_key, search_term, date):
        url = f"https://breachsense.io/api?lic={api_key}&s={search_term}&strict&json"
        if date:
            url = f"https://breachsense.io/api?lic={api_key}&s={search_term}&strict&json&date={date}"   
        try: 
            response = requests.get(url)
            return response.text
        except Exception as e:
            return "Exception occured: %s" % e

if __name__ == "__main__":
    asyncio.run(BreachSense.run(), debug=True)
