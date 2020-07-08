import socket
import asyncio
import time
import random
import json
import requests

from walkoff_app_sdk.app_base import AppBase

class Siemonster(AppBase):
    __version__ = "1.0.0"
    app_name = "siemonster"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    async def ping(self):
        message = f"SIEMonster welcomes from {socket.gethostname()} in workflow {self.current_execution_id}!"

        # This logs to the docker logs
        self.logger.info(message)

        return message

    async def es_get_cluster_health(self, url):
        return requests.get(url + "/_cluster/health", verify=False).text

    async def es_query(self, method, url, path, body):
        headers = {
            "Accept": "application/json",
            "Content-type": "application/json",
        }
        return requests.request(method, url + path, data=body, headers=headers, verify=False).text

if __name__ == "__main__":
    asyncio.run(Siemonster.run(), debug=True)
