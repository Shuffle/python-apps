
import base64
import email.utils
import hmac
import hashlib
import urllib
import requests
import json
from walkoff_app_sdk.app_base import AppBase


class DuoSecurity(AppBase):
    __version__ = "1.0.0"
    app_name = "DuoSecurity"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    def sign(self, secret_key, itegration_key, api_host, method, path, params):
        """
            Return HTTP Basic Authentication ("Authorization" and "Date") headers.
            method, host, path: strings from request
            params: dict of request parameters
            skey: secret key
            ikey: integration key
        """
        # create canonical string
        now = email.utils.formatdate()
        canon = [now, method.upper(), api_host.lower(), path]
        args = []
        for key in sorted(params.keys()):
            val = params[key].encode("utf-8")
            args.append(
                '%s=%s' % (urllib.parse.
                           quote(key, '~'), urllib.parse.quote(val, '~')))
        canon.append('&'.join(args))
        canon = '\n'.join(canon)

        # sign canonical string
        sig = hmac.new(bytes(secret_key, encoding='utf-8'),
                       bytes(canon, encoding='utf-8'),
                       hashlib.sha1)
        print("sig", sig.hexdigest())
        print("intergration key", itegration_key)
        auth = '%s:%s' % (itegration_key, sig.hexdigest())

        # return headers
        print("base",base64.b64encode(bytes(auth, encoding="utf-8")).decode())
        return {'Date': now, 'Authorization': 'Basic %s' % base64.b64encode(bytes(auth, encoding="utf-8")).decode()}

    # Function to verify that Duo is up before trying to call other Auth API endpoints
    def Ping(self, secret_key, itegration_key, api_host):
        path = "/auth/v2/ping"
        request_url = f"{api_host}{path}"
        params = {}
        headers = self.sign(secret_key, itegration_key,
                            api_host, "GET", path, params)
        request_headers = {'Content-Type': 'application/json',
                           'Authorization': f"{headers['Authorization']}", 'Date': f"{headers['Date']}"}
        try:
            response = requests.get(
                request_url, headers=request_headers, verify=False)
            print(response)
            res = json.loads(response.text)
            print(res)
            return res
        except Exception as e:
            return json.dumps({"success": "false", "message": str(e)})

    # Function to verify that the Auth API integration and secret keys are valid, and that the signature is being generated properly
    def Check(self, secret_key, itegration_key, api_host):
        path = "/auth/v2/check"
        request_url = f"{api_host}{path}"
        params = {}
        headers = self.sign(secret_key, itegration_key,
                            api_host, "GET", path,params)

        print(headers['Date'])
        print(headers['Authorization'])
        request_headers = {"Content-Type": "application/x-www-form-urlencoded","Date": f"{headers['Date']}","Authorization": f"{headers['Authorization']}"}
        try:
            response = requests.get(
                request_url, headers=request_headers, verify=True)
            res = json.loads(response.content.decode())
            return res
        except Exception as e:
            return json.dumps({"success": "false", "message": str(e)})

    # Function provides a programmatic way to retrieve your stored logo.
    def GetLogo(self, secret_key, itegration_key, api_host):
        path = "/auth/v2/logo"
        params = {}
        request_url = f"{api_host}{path}"
        headers = self.sign(secret_key, itegration_key,
                            api_host, "GET", path, params)
        request_headers = {'Content-Type': 'application/json',
                           'Authorization': f"{headers.get('Authorization')}", 'Date': f"{headers.get('Date')}"}
        try:
            response = requests.get(
                request_url, headers=request_headers, verify=False)
            res = json.loads(response.content.decode())
            return res
        except Exception as e:
            return json.dumps({"success": "false", "message": str(e)})

    # Function provides a programmatic way to enroll new users with Duo two-factor authentication. It creates the user in Duo and returns a code (as a QR code) that Duo Mobile can scan with its built-in camera. Scanning the QR code adds the user's account to the app so that they receive and respond to Duo Push login requests.
    def EnrollNewUser(self, secret_key, itegration_key, api_host, username):
        path = "/auth/v2/enroll"
        params = {"username": username}
        request_url = f"{api_host}{path}"

        headers = self.sign(secret_key, itegration_key,api_host, "POST", path, params)

        request_headers = {"Content-Type": "application/x-www-form-urlencoded",
                           "Authorization": f"{headers['Authorization']}", 'Date': f"{headers['Date']}"}
        
        print(headers['Authorization'])
        print(headers['Date'])

        payload = json.dumps(params)
        try:
            response = requests.request(
                "POST", request_url, headers=request_headers, data=payload)
            res = json.loads(response.content.decode())
            return res
        except Exception as e:
            return json.dumps({"success": "false", "message": str(e)})

    # Check whether a user has completed enrollment.
    def GetEnrollStatus(self, secret_key, itegration_key, api_host, user_id, activation_code):
        path = "/auth/v2/enroll_status"
        params = {
            "user_id": user_id,
            "activation_code": activation_code
        }
        request_url = f"{api_host}{path}"

        headers = self.sign(secret_key, itegration_key,
                            api_host, "POST", path, params)

        request_headers = {'Content-Type': 'application/json',
                           'Authorization': f"{headers['Authorization']}", 'Date': f"{headers['Date']}"}

        payload = json.dumps(params)
        try:
            response = requests.request(
                "POST", request_url, headers=request_headers, data=payload)
            res = json.loads(response.content.decode())
            return res
        except Exception as e:
            return json.dumps({"success": "false", "message": str(e)})

    # Function determines whether a user is authorized to log in, and (if so) returns the user's available authentication factors.
    def PreAuthCheck(self, secret_key, itegration_key, api_host, user_id, username):
        path = "/auth/v2/preauth"
        params = {
            "user_id": user_id,
            "username": username
        }
        request_url = f"{api_host}{path}"

        headers = self.sign(secret_key, itegration_key,
                            api_host, "POST", path, params)

        request_headers = {'Content-Type': 'application/json',
                           'Authorization': f"{headers['Authorization']}", 'Date': f"{headers['Date']}"}

        payload = json.dumps(params)
        try:
            response = requests.request(
                "POST", request_url, headers=request_headers, data=payload)
            res = json.loads(response.content.decode())
            return res
        except Exception as e:
            return json.dumps({"success": "false", "message": str(e)})

    # Function performs second-factor authentication for a user by sending a push notification to the user's smartphone app, verifying a passcode, or placing a phone call. It is also used to send the user a new batch of passcodes via SMS.
    def Auth(self, secret_key, itegration_key, api_host, user_id, username, factor, device, passcode):
        path = "/auth/v2/auth"
        params = {
            "user_id": user_id,
            "username": username,
            "factor": factor,
            "device": device,
            "passcode": passcode
        }
        request_url = f"{api_host}{path}"

        headers = self.sign(secret_key, itegration_key,
                            api_host, "POST", path, params)

        request_headers = {'Content-Type': 'application/json',
                           'Authorization': f"{headers['Authorization']}", 'Date': f"{headers['Date']}"}

        payload = json.dumps(params)
        try:
            response = requests.request(
                "POST", request_url, headers=request_headers, data=payload)
            res = json.loads(response.content.decode())
            return res
        except Exception as e:
            return json.dumps({"success": "false", "message": str(e)})

    # Function "long-polls" for the next status update from the authentication process for a given transaction. That is to say, if no status update is available at the time the request is sent, it will wait until there is an update before returning a response.
    def GetAuthStatus(self, secret_key, itegration_key, api_host, txid):
        path = "/auth/v2/auth_status"
        params = {
            "txid": txid
        }
        request_url = f"{api_host}{path}"
        headers = self.sign(secret_key, itegration_key,
                            api_host, "GET", path, params)
        request_headers = {'Content-Type': 'application/json',
                           'Authorization': f"{headers['Authorization']}", 'Date': f"{headers['Date']}"}
        try:
            response = requests.get(
                request_url, headers=request_headers, verify=False)
            res = json.loads(response.content.decode())
            return res
        except Exception as e:
            return json.dumps({"success": "false", "message": str(e)})


if __name__ == "__main__":
    DuoSecurity.run()
