import requests
import socket
import json

socket.setdefaulttimeout(10)
from walkoff_app_sdk.app_base import AppBase


class CrtShRunner(AppBase):
    __version__ = "1.0.0"
    app_name = "Crt.sh search"

    def __init__(self, redis, logger, console_logger=None):
        super().__init__(redis, logger, console_logger)

    def search_identity(self, identity, exclude_expired):

        cturl = "https://crt.sh?q={}&output=json"
        if exclude_expired.lower() == "true":
            cturl = cturl + "&exclude=expired"
        cturl = cturl.format(identity)

        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 ' \
             'Safari/537.36 '

        try:
            response = requests.get(cturl, headers={'User-Agent': ua})
            if response.ok:
                return json.loads(response.content.decode('utf-8'))
            else:
                return {"success": False, "message": "The request failed", "reason": response.reason}
        except requests.exceptions.HTTPError as e:
            print(e)
            return {"success": False, "message": e}
        except requests.exceptions.RequestException as e:
            print(e)
            return {"success": False, "message": e}


if __name__ == "__main__":
    CrtShRunner.run()
