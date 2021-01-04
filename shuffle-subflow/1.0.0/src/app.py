import socket
import asyncio
import time
import random
import json
import requests

from walkoff_app_sdk.app_base import AppBase

class Subflow(AppBase):
    """
    An example of a Walkoff App.
    Inherit from the AppBase class to have Redis, logging, and console logging set up behind the scenes.
    """
    __version__ = "1.0.0"
    app_name = "hello_world"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    async def run_subflow(self, user_apikey, workflow, argument):
        url = "%s/api/v1/workflows/%s/execute" % (self.url, workflow)
        headers = {
            "Authorization": "Bearer %s" % user_apikey,
        }

        try:
            ret = requests.post(url, headers=headers, json=argument)
            print("Successfully sent as JSON")
        except:
            ret = requests.post(url, headers=headers, data=argument)
            print("Successfully sent as data")

        print("Status: %d" % ret.status_code)
        print("RET: %s" % ret.text)

        return ret.text

        # This logs to the docker logs
        #self.logger.info(message)

        return message

if __name__ == "__main__":
    asyncio.run(Subflow.run(), debug=True)
