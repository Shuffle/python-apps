from os import access
import socket
import time
import random
import json
import requests

from walkoff_app_sdk.app_base import AppBase


class PrismaCloud(AppBase):
    __version__ = "1.0.1"
    app_name = "Prisma Cloud"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    # Prisma Cloud Authentication - Get JWT Token before injecting into header

    def get_jwt(self, url, accesskey, secretkey):
        headers = {
            "accept": "application/json; charset=UTF-8",
            "content-type": "application/json; charset=UTF-8"
        }
        payload = "{\"username\":\"" + accesskey + \
            "\",\"password\":\"" + secretkey + "\"}"
        response = requests.request(
            "POST", url+"/login", headers=headers, data=payload)
        if response.status_code != 200:
            print("Prisma cloud token is wrong or expired boy! status code : " +
                  str(response.status_code))
        else:
            print("Ok for the prisma token")
        return response.json()["token"]

    # Prisma Cloud Authentication - Make the header with the JWT Token - Valid for 10 minutes

    def generate_prisma_header(self, url, accesskey, secretkey):
        headers = {
            "accept": "*/*",
            "x-redlock-auth": self.get_jwt(url, accesskey, secretkey)
        }
        return headers

    def get_alert(self, url, accesskey, secretkey, alertId):
        suffix = "/alert/" + str(alertId)
        # headers = {
        # 'Content-Type': 'application/json',
        # 'x-redlock-auth': self.get_jwt(url, accesskey, secretkey)
        # }
        headers = self.generate_prisma_header(url, accesskey, secretkey)
        try:
            r = requests.get(url + suffix, headers=headers)
            return json.dumps(r.json())
        except Exception as e:
            return e.__class__

    def remediate_alert(self, url, accesskey, secretkey, alertId):
        suffix = "/alert/remediation/" + str(alertId)
        headers = self.generate_prisma_header(url, accesskey, secretkey)
        try:
            r = requests.request("PATCH", url+suffix, headers=headers)
            interpretation = "None"
            success = True
            if r.status_code == 200:
                interpretation = "Alert was successfully remediated"
            elif r.status_code == 405:
                success = False
                interpretation = "Alert was already remediated or cannot be remediated"
            else:
                success = False
                interpretation = "This status code is not usual and execution isn't guaranteed to have worked : " + r.status_code
                raise Exception(interpretation)
            message = {
                "success": success,
                "alertId": str(alertId),
                "prismaResponse": str(r.text),
                "statusCode": str(r.status_code),
                "message": str(interpretation)
            }
            return json.dumps(message)
        except Exception as e:
            return e.__class__

    def dismiss_alert(self, url, accesskey, secretkey, alertId, dismissalNote):
        suffix = "/alert/dismiss"
        headers = self.generate_prisma_header(url, accesskey, secretkey)
        try:
            payload = {"alerts": [alertId], "dismissalNote": dismissalNote,
                       "filter": {"filters": None, "timeRange": None}, "policies": []}
            r = requests.post(url + suffix, json=payload, headers=headers)
            interpretation = "None"
            success = False
            if r.status_code == 200:
                success = True
                interpretation = "Alert was successfully dismissed"
            elif r.status_code == 400:
                interpretation = "missing or invalid parameter value, internal error.."
                raise Exception(interpretation)
            elif r.status_code == 403:
                interpretation = "permission error"
                raise Exception(interpretation)
            elif r.status_code == 404:
                interpretation = "alert no longer in expected state"
                # raise Exception(interpretation)
            else:
                interpretation = "oops, something went wrong... no idea!"
                raise Exception(interpretation)
            message = {
                "success": success,
                "alertId": str(alertId),
                "prismaResponse": str(r.text),
                "statusCode": str(r.status_code),
                "message": str(interpretation)
            }
            return json.dumps(message)
        except Exception as e:
            return e.__class__


if __name__ == "__main__":
    PrismaCloud.run()

