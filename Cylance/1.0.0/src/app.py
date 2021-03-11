import socket
import asyncio
import time
import random
import json
import requests
import jwt 
import uuid
import json
from datetime import datetime, timedelta

from walkoff_app_sdk.app_base import AppBase

class Cylance(AppBase):
    __version__ = "1.0.0"
    app_name = "Cylance"  


    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    # This system is fucking stupid - every developer ever :)
    def auth(self, app_id, app_secret, tid_val):
        timeout = 1800
        now = datetime.utcnow()
        timeout_datetime = now + timedelta(seconds=timeout)
        epoch_time = int((now - datetime(1970, 1, 1)).total_seconds())
        epoch_timeout = int((timeout_datetime - datetime(1970, 1, 1)).total_seconds())
        jti_val = str(uuid.uuid4())
        AUTH_URL = "https://protectapi.cylance.com/auth/v2/token"
        claims = {
            "exp": epoch_timeout,
            "iat": epoch_time,
            "iss": "http://cylance.com",
            "sub": app_id,
            "tid": tid_val,
            "jti": jti_val,
            #"scp": ["policy:create","policy:list","policy:read","policy:update"]
        }

        encoded = jwt.encode(claims, app_secret, algorithm='HS256').decode('utf-8')
        payload = {"auth_token": encoded}
        headers = {"Content-Type": "application/json; charset=utf-8"}
        resp = requests.post(AUTH_URL, headers=headers, data=json.dumps(payload))
        auth_token = resp.json()["access_token"]
        return auth_token

    async def get_threat(self, app_id, app_secret, tenant_id, threat_id):
        auth_token = self.auth(app_id, app_secret, tenant_id)
        url = f"https://protectapi.cylance.com/threats/v2/{threat_id}"
        params = {}

        headers = {
            "Authorization": f"Bearer {auth_token}"
        }

        resp = requests.get(url, headers=headers, params=params)
        return resp.text

    async def get_detection(self, app_id, app_secret, tenant_id, detection_id):
        auth_token = self.auth(app_id, app_secret, tenant_id)
        url = f"https://protectapi.cylance.com/detections/v2/{detection_id}"
        params = {}

        headers = {
            "Authorization": f"Bearer {auth_token}"
        }

        resp = requests.get(url, headers=headers, params=params)
        return resp.text

    async def list_threats(self, app_id, app_secret, tenant_id, page=1, page_size=20):
        auth_token = self.auth(app_id, app_secret, tenant_id)

        if page == 0 or page == "":
            page = 1
        if page_size == 0 or page_size == "":
            page_size = 20

        url = "https://protectapi.cylance.com/threats/v2"
        params = {
            "page": page,
            "page_size": page_size,
        }
        params = {}

        headers = {
            "Authorization": f"Bearer {auth_token}"
        }

        resp = requests.get(url, headers=headers, params=params)
        return resp.text

    async def list_detections(self, app_id, app_secret, tenant_id, page=1, page_size=20):
        auth_token = self.auth(app_id, app_secret, tenant_id)

        if page == 0 or page == "":
            page = 1
        if page_size == 0 or page_size == "":
            page_size = 20

        url = "https://protectapi.cylance.com/detections/v2"
        params = {
            "page": page,
            "page_size": page_size,
        }
        params = {}

        headers = {
            "Authorization": f"Bearer {auth_token}"
        }

        resp = requests.get(url, headers=headers, params=params)
        return resp.text
        print(resp.text)
        print(resp.status_code)
    

if __name__ == "__main__":
    asyncio.run(Cylance.run(), debug=True)
