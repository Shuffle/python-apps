import time
import json
import json
import random
import socket
import uncurl
import asyncio
import requests

from walkoff_app_sdk.app_base import AppBase

class HTTP(AppBase):
    __version__ = "1.0.0"
    app_name = "http"  

    def __init__(self, redis, logger, console_logger=None):
        print("INIT")
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    # This is dangerously fun :)
    async def curl(self, statement):
        try: 
            if not statement.startswith("curl "):
                statement = "curl %s" % statement

            data = uncurl.parse(statement)
            request = eval(data)
            if isinstance(request, requests.models.Response):
                return request.text
            else:
                return "Unable to parse the curl parameter. Remember to start with curl "
        except:
            return "An error occurred during curl parsing"

    def splitheaders(self, headers):
        parsed_headers = {}
        if headers:
            split_headers = headers.split("\n") 
            self.logger.info(split_headers)
            for header in split_headers:
                if ": " in header:
                    splititem = ": "
                elif ":" in header:
                    splititem = ":"
                elif "= " in header:
                    splititem = "= "
                elif "=" in header:
                    splititem = "="
                else:
                    self.logger.info("Skipping header %s as its invalid" % header)
                    continue

                splitheader = header.split(splititem)
                if len(splitheader) == 2:
                    parsed_headers[splitheader[0]] = splitheader[1]
                else:
                    self.logger.info("Skipping header %s with split %s cus only one item" % (header, splititem))
                    continue

        return parsed_headers

    def checkverify(self, verify):
        if verify == None:
            return False
        elif verify:
            return True
        elif not verify:
            return False
        elif verify.lower().strip() == "false":
            return False
        else:
            return True 

    def checkbody(self, body):
        # Indicates json
        if body.strip().startswith("{"):
            body = body.replace("\'", "\"")

            # Not sure if loading is necessary
            # Seemed to work with plain string into data=body too, and not parsed json=body
            #try:
            #    body = json.loads(body)
            #except json.decoder.JSONDecodeError as e:
            #    return body

            return body
        else:
            return body

    async def GET(self, url, headers="", verify=True):
        parsed_headers = self.splitheaders(headers)
        verify = self.checkverify(verify)
        return requests.get(url, headers=parsed_headers, verify=verify).text

    async def POST(self, url, headers="", body="", verify=True):
        parsed_headers = self.splitheaders(headers)
        verify = self.checkverify(verify)
        body = self.checkbody(body)
        return requests.post(url, headers=parsed_headers, data=body, verify=verify).text

    # UNTESTED BELOW HERE
    async def PUT(self, url, headers="", body="", verify=True):
        parsed_headers = self.splitheaders(headers)
        verify = self.checkverify(verify)
        body = self.checkbody(body)
        return requests.put(url, headers=parsed_headers, data=body, verify=verify).text

    async def PATCH(self, url, headers="", body="", verify=True):
        parsed_headers = self.splitheaders(headers)
        verify = self.checkverify(verify)
        body = self.checkbody(body)
        return requests.patch(url, headers=parsed_headers, data=body, verify=verify).text

    async def DELETE(self, url, headers="", body="", verify=True):
        parsed_headers = self.splitheaders(headers)
        verify = self.checkverify(verify)
        return requests.delete(url, headers=parsed_headers, verify=verify).text

    async def HEAD(self, url, headers="", body="", verify=True):
        parsed_headers = self.splitheaders(headers)
        verify = self.checkverify(verify)
        body = self.checkbody(body)
        return requests.head(url, headers=parsed_headers, verify=verify).text

    async def OPTIONS(self, url, headers="", body="", verify=True):
        parsed_headers = self.splitheaders(headers)
        verify = self.checkverify(verify)
        body = self.checkbody(body)
        return requests.options(url, headers=parsed_headers, verify=verify).text


# Run the actual thing after we've checked params
def run(request):
    print("Starting cloud!")
    action = request.get_json() 
    print(action)
    print(type(action))
    authorization_key = action.get("authorization")
    current_execution_id = action.get("execution_id")
	
    if action and "name" in action and "app_name" in action:
        asyncio.run(HTTP.run(action), debug=True)
        return f'Attempting to execute function {action["name"]} in app {action["app_name"]}' 
    else:
        return f'Invalid action'

if __name__ == "__main__":
    asyncio.run(HTTP.run(), debug=True)
