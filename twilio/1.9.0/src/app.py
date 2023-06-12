import json
import ast
import requests

from walkoff_app_sdk.app_base import AppBase

class TWILIO(AppBase):
    __version__ = "1.9.0"
    app_name = "twilio"

    def __init__(self, redis, logger, console_logger=None):
        print("INIT")
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

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

    def checkbody(self, body):
        # Indicates json
        if isinstance(body, str):
            if body.strip().startswith("{"):
                body = json.dumps(ast.literal_eval(body))


                # Not sure if loading is necessary
                # Seemed to work with plain string into data=body too, and not parsed json=body
                #try:
                #    body = json.loads(body)
                #except json.decoder.JSONDecodeError as e:
                #    return body

                return body
            else:
                return body

        if isinstance(body, dict) or isinstance(body, list):
            try:
                body = json.dumps(body)
            except:
                return body

        return body

    def fix_url(self, url):
        # Random bugs seen by users
        if "hhttp" in url:
            url = url.replace("hhttp", "http")

        if "http:/" in url and not "http://" in url:
            url = url.replace("http:/", "http://", -1)
        if "https:/" in url and not "https://" in url:
            url = url.replace("https:/", "https://", -1)
        if "http:///" in url:
            url = url.replace("http:///", "http://", -1)
        if "https:///" in url:
            url = url.replace("https:///", "https://", -1)
        if not "http://" in url and not "http" in url:
            url = f"http://{url}"

        return url

    def return_file(self, requestdata):
        filedata = {
            "filename": "response.txt",
            "data": requestdata,
        }
        fileret = self.set_files([filedata])
        if len(fileret) == 1:
            return {"success": True, "file_id": fileret[0]}

        return fileret

    def prepare_response(self, request):
        try:
            parsedheaders = {}
            for key, value in request.headers.items():
                parsedheaders[key] = value

            cookies = {}
            if request.cookies:
                for key, value in request.cookies.items():
                    cookies[key] = value


            jsondata = request.text
            try:
                jsondata = json.loads(jsondata)
            except:
                pass

            return {
                "success": True,
                "status": request.status_code,
                "url": request.url,
                "headers": parsedheaders,
                "body": jsondata,
                "cookies":cookies,
            }
        except Exception as e:
            print(f"[WARNING] Failed in request: {e}")
            return {
                "success": False,
                "status": "XXX",
                "error": request.text
            }


    def summarize_responses(self, one_response, summary):
        summary["results"].append(one_response)

        # if ONE request fails, summary is marked as failed
        if False == one_response["success"]:
            summary["success"] = False

        # if one status code is not 200, use this failure status code for summary
        if "200" != one_response["status"]:
            summary["status"] = one_response["status"]

        return summary


    def Send_SMS(self, url, headers="", username="", password="", body="", From="", To="", timeout=5):
        url = self.fix_url(url)

        parsed_headers = self.splitheaders(headers)
        parsed_headers["User-Agent"] = "Shuffle Automation"
        body = self.checkbody(body)

        auth=None
        if username or password:
            # Shouldn't be used if authorization headers exist
            if "Authorization" in parsed_headers:
                #print("Found authorization - skipping username & pw")
                pass
            else:
                auth = requests.auth.HTTPBasicAuth(username, password)

        if not timeout:
            timeout = 5
        if timeout:
            timeout = int(timeout)

        summary = {
            "success": True,
            "status": "200",
            "url": url,
            "results": []
        }

        # send Twilio API request for every single receiver number
        for receiver in To.split(","):
            data = {'Body' : body, 'From' : From, 'To' : receiver.strip()}
            request = requests.post(url, headers=parsed_headers, auth=auth, data=data, timeout=timeout)
            response = self.prepare_response(request)
            summary = self.summarize_responses(response, summary)

        return json.dumps(summary)


# Run the actual thing after we've checked params
def run(request):
    print("Starting cloud!")
    action = request.get_json()
    print(action)
    print(type(action))
    authorization_key = action.get("authorization")
    current_execution_id = action.get("execution_id")

    if action and "name" in action and "app_name" in action:
        TWILIO.run(action)
        return f'Attempting to execute function {action["name"]} in app {action["app_name"]}'
    else:
        return f'Invalid action'

if __name__ == "__main__":
    TWILIO.run()
