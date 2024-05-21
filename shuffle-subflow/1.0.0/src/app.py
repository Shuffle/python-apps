import json
import requests

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
    def run_userinput(self, user_apikey, sms="", email="", subflow="", information="", startnode="", backend_url="", source_node=""):
        #url = "%s/api/v1/workflows/%s/execute" % (self.url, workflow)

        headers = {
            "Authorization": "Bearer %s" % user_apikey,
            "User-Agent": "Shuffle Userinput 1.1.0"
        }

        result = {
            "success": True,
            "source": "userinput",
            "reason": "Userinput data sent and workflow paused. Waiting for user input before continuing workflow.",
            "information": information,
            "click_info": {
                "clicked": False,
                "time": "",
                "ip": "",
                "user": "", 
                "note": "",
            }
        }

        url = self.url
        if len(self.base_url) > 0:
            url = self.base_url

        if len(str(backend_url)) > 0:
            url = backend_url

        print("Found backend url: %s" % url)
        #if len(information):
        #    print("Should run arg: %s", information)

        if len(subflow):
            #print("Should run subflow: %s", subflow) 

            # Missing startnode (user input trigger)
            #print("Subflows to run from userinput: ", subflows)

            subflows = subflow.split(",")
            frontend_url = url
            if ":5001" in frontend_url:
                print("Should change port to 3001.")
            if "appspot.com" in frontend_url:
                frontend_url = "https://shuffler.io"

            for item in subflows: 
                # In case of URL being passed, and not just ID
                if "/" in item:
                    item = item.split("/")[-1]

                # Subflow should be the subflow to run
                # Workflow in the URL should be the source workflow
                argument = json.dumps({
                    "information": information,
                    "parent_workflow": self.full_execution["workflow"]["id"],
                    "frontend_continue": "%s/workflows/%s/run?authorization=%s&reference_execution=%s&answer=true" % (frontend_url, self.full_execution["workflow"]["id"], self.full_execution["authorization"], self.full_execution["execution_id"]),
                    "frontend_abort": "%s/workflows/%s/run?authorization=%s&reference_execution=%s&answer=false" % (frontend_url, self.full_execution["workflow"]["id"], self.full_execution["authorization"], self.full_execution["execution_id"]),
                    "api_continue": "%s/api/v1/workflows/%s/execute?authorization=%s&reference_execution=%s&answer=true" % (frontend_url, self.full_execution["workflow"]["id"], self.full_execution["authorization"], self.full_execution["execution_id"]),
                    "api_abort": "%s/api/v1/workflows/%s/execute?authorization=%s&reference_execution=%s&answer=false" % (frontend_url, self.full_execution["workflow"]["id"], self.full_execution["authorization"], self.full_execution["execution_id"]),
                })

                ret = self.run_subflow(user_apikey, item, argument, source_workflow=self.full_execution["workflow"]["id"], source_execution=self.full_execution["execution_id"], source_auth=self.full_execution["authorization"], startnode=startnode, backend_url=backend_url, source_node=source_node)
                result["subflow"] = ret 
                result["subflow_url"] = "%s/workflows/%s" % (frontend_url, item)

        if len(email):
            jsondata = {
                "targets": [],
                "body": information,
                "subject": "User input required",
                "type": "User input",
                "start": startnode,
                "workflow_id": self.full_execution["workflow"]["id"],
                "reference_execution": self.full_execution["execution_id"],
                "authorization": self.full_execution["authorization"],
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
                "authorization": self.full_execution["authorization"],
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



        return json.dumps(result)

    def run_subflow(self, user_apikey, workflow, argument, source_workflow="", source_execution="", source_node="", source_auth="", startnode="", backend_url="", auth_override=""):
        #print("STARTNODE: %s" % startnode)
        url = "%s/api/v1/workflows/%s/execute" % (self.url, workflow)
        if len(self.base_url) > 0:
            url = "%s/api/v1/workflows/%s/execute" % (self.base_url, workflow)

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

        if len(self.full_execution["execution_id"]) > 0 and self.full_execution["execution_id"] != source_execution:
            params["source_execution"] = self.full_execution["execution_id"]

        if len(self.full_execution["authorization"]) > 0 and self.full_execution["authorization"] != source_auth:
            params["source_auth"] = self.full_execution["authorization"]

        if len(str(backend_url)) > 0:
            url = "%s/api/v1/workflows/%s/execute" % (backend_url, workflow)
            print("[INFO] Changed URL to %s for this execution" % url)
        
        headers = {
            "Authorization": "Bearer %s" % user_apikey,
            "User-Agent": "Shuffle Subflow 1.0.0"
        }

        if len(auth_override) > 0:
            headers["appauth"] = auth_override

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
