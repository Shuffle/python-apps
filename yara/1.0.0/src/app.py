import socket
import asyncio
import time
import random
import json
import requests
import yara

from walkoff_app_sdk.app_base import AppBase

class Yara(AppBase):
    __version__ = "1.0.0"
    app_name = "yara"  

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    # Write your data inside this function
    #https://yara.readthedocs.io/en/latest/yarapython.html
    async def analyze_file(self, file_id):
        print("Getting file: %s" % file_id)
        file_ret = self.get_file(file_id)
        print("FINISHED GETTING FILE: %s" % file_ret)
        rules = yara.compile("/rules")
        #rules.match(file)

        matches = rules.match(data=file_ret["data"], timeout=60)
        print(matches)

        return matches 

if __name__ == "__main__":
    asyncio.run(Yara.run(), debug=True)
