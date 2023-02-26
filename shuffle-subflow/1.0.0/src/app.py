import asyncio
import time
import random
import json
import requests
import json

from walkoff_app_sdk.app_base import AppBase

class Subflow(AppBase):
    """
    An example of a Walkoff App.
    Inherit from the AppBase class to have Redis, logging, and console logging set up behind the scenes.
    """
    __version__ = "1.0.0"
    app_name = "subflow"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    # Should run user input
    def run_userinput(self, user_apikey, sms="", email="", subflow="", information="", startnode="", backend_url=""):
        #url = "%s/api/v1/workflows/%s/execute" % (self.url, workflow)

        headers = {
            "Authorization": "Bearer %s" % user_apikey,
            "User-Agent": "Shuffle Userinput 1.0.0"
        }

        result = {
            "success": True,
            "source": "userinput",
            "reason": "Userinput data sent and workflow paused. Waiting for user input before continuing workflow."
        }

        url = self.url
        if len(str(backend_url)) > 0:
            url = "%s" % (backend_url)

        if len(email):
            jsondata = {
                "targets": [],
                "body": information,
                "subject": "User input required",
                "type": "User input",
                "start": startnode,
                "workflow_id": self.full_execution["workflow"]["id"],
                "reference_execution": self.full_execution["execution_id"],
            }

            for item in email.split(","):
                jsondata["targets"].append(item.strip())

            print("Should run email with targets: %s", jsondata["targets"])

            ret = requests.post("%s/api/v1/functions/sendmail" % url, json=jsondata, headers=headers)
            if ret.status_code != 200:
                print("Failed sending email. Data: %s" % ret.text)
                result["email"] = False 
            else:
                result["email"] = True

        if len(sms) > 0:
            print("Should run SMS: %s", sms)

            jsondata = {
                "numbers": [],
                "body": information,
                "type": "User input",
                "start": startnode,
                "workflow_id": self.full_execution["workflow"]["id"],
                "reference_execution": self.full_execution["execution_id"],
            }

            for item in sms.split(","):
                jsondata["numbers"].append(item.strip())

            print("Should send sms with targets: %s", jsondata["numbers"])

            ret = requests.post("%s/api/v1/functions/sendsms" % url, json=jsondata, headers=headers)
            if ret.status_code != 200:
                print("Failed sending email. Data: %s" % ret.text)
                result["sms"] = False 
            else:
                result["sms"] = True

        if len(subflow):
            print("Should run subflow: %s", subflow) 

        if len(information):
            print("Should run arg: %s", information)

        return json.dumps(result)

    def run_subflow(self, user_apikey, workflow, argument, source_workflow="", source_execution="", source_node="", source_auth="", startnode="", backend_url=""):
        #print("STARTNODE: %s" % startnode)
        url = "%s/api/v1/workflows/%s/execute" % (self.url, workflow)

        params = {}
        if len(str(source_workflow)) > 0:
            params["source_workflow"] = source_workflow
        else:
            print("No source workflow")

        if len(str(source_auth)) > 0:
            params["source_auth"] = source_auth
        else:
            print("No source auth")

        if len(str(source_node)) > 0:
            params["source_node"] = source_node
        else:
            print("No source node")

        if len(str(source_execution)) > 0:
            params["source_execution"] = source_execution
        else:
            print("No source execution")

        if len(str(startnode)) > 0:
            params["start"] = startnode 
        else:
            print("No startnode")

        if len(str(backend_url)) > 0:
            url = "%s/api/v1/workflows/%s/execute" % (backend_url, workflow)
            print("[INFO] Changed URL to %s for this execution" % url)
        
        headers = {
            "Authorization": "Bearer %s" % user_apikey,
            "User-Agent": "Shuffle Subflow 1.0.0"
        }

        if len(str(argument)) == 0:
            ret = requests.post(url, headers=headers, params=params)
        else:
            if not isinstance(argument, list) and not isinstance(argument, dict):
                try:
                    argument = json.loads(argument)
                except:
                    pass

            #print(f"ARG: {argument}")
            try:
                ret = requests.post(url, headers=headers, params=params, json=argument)
                print(f"Successfully sent argument of length {len(str(argument))} as JSON")
            except:
                try:
                    ret = requests.post(url, headers=headers, json=argument, params=params)
                    print("Successfully sent as JSON (2)")
                except:
                    ret = requests.post(url, headers=headers, data=argument, params=params)
                    print("Successfully sent as data (3)")

        print("Status: %d" % ret.status_code)
        print("RET: %s" % ret.text)

        return ret.text

if __name__ == "__main__":
    Subflow.run()
