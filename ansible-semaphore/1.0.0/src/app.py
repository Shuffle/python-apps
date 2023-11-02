import socket
import asyncio
import time
import random
import json
import requests

from walkoff_app_sdk.app_base import AppBase

class AnsibleSemaphore(AppBase):
    __version__ = "1.0.0"
    app_name = "ansible_semaphore"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)


    # Write your data inside this function
    def login(self, url, username, password):
        # It comes in as a string, so needs to be set to JSON
        login_url = url + "/api/auth/login"
        headers = {'Content-Type': 'application/json','Accept': 'application/json'}
        body = {"auth": username, "password": password}
        try:
            res = requests.post(login_url, headers=headers, data=json.dumps(body))
        except Exception as e:
            return "Couldn't generate cookies: %s" % e
        
        return res.cookies.get_dict()
    
    def logout(self, token):
        # It comes in as a string, so needs to be set to JSON
        login_url = url + "/api/auth/logout"
        headers = {'Content-Type': 'application/json','Accept': 'application/json', 'Authorization': 'Bearer ' + token}
        try:
            res = requests.post(login_url, headers=headers)
        except Exception as e:
            return "Couldn't decode json: %s" % e
        
        #print(f"logged out: {res.status_code}")

    def create_token(self, url, username, password):
        cookies = self.login(url, username, password)
        try:
            res = requests.post(url + "/api/user/tokens", cookies=cookies)
        except Exception as e:
            return "error in fetching token: %s" % e
        
        if res.status_code == 201:
            return res.json()["id"]
        else:
            print("error in fetching token: ", res.status_code)
            return False

    def delete_token(self, url, token):
        headers = {'Content-Type': 'application/json','Accept': 'application/json', 'Authorization': 'Bearer ' + token}
        try:
            res = requests.delete(url + "/api/user/tokens/" + token)
        except Exception as e:
            return "error in deleting token: %s" % e
        return res.status_code
        
    def list_inventories(self, url, username, password , project_id):
        inventory_url = f"{url}/api/project/{project_id}/inventory"
        token = self.create_token(url, username, password)

        if token == False:
            return {"success":"false","message":"could not generate token"}

        headers = {"Content-Type": "application/json","Accept": "application/json", "Authorization": "Bearer " + token}
        
        body = {
            "sort":"name",
            "order":"asc",
            "project_id": int(project_id)
        }
        try:
            res = requests.get(inventory_url, headers=headers,data=json.dumps(body))
        except Exception as e:
            return {"success":"false","message":e}
        
        self.logout(token)
        return res.json()
    
    def list_tasks(self, url, username, password , project_id):
        task_url = f"{url}/api/project/{project_id}/tasks"
        token = self.create_token(url, username, password)

        if token == False:
            return {"success":"false","message":"could not generate token"}

        headers = {"Content-Type": "application/json","Accept": "application/json", "Authorization": "Bearer " + token}
        
        # body = {
        #     "sort":"name",
        #     "order":"asc",
        #     "project_id": int(project_id)
        # }
        try:
            res = requests.get(task_url, headers=headers)
        except Exception as e:
            return {"success":"false","message":e}
        
        self.logout(token)
        return res.json()
    
    def run_task(self, url, username, password, project_id, template_id, debug, dryrun):

        debug = True if debug in ["true", "True"] else False
        dryrun = True if dryrun in ["true", "True"] else False

        inventory_url = f"{url}/api/project/{project_id}/tasks"
        token = self.create_token(url, username, password)

        if token == False:
            return {"success":"false","message":"could not generate token"}

        headers = {"Content-Type": "application/json","Accept": "application/json", "Authorization": "Bearer " + token}
        
        body = {
            "template_id": int(template_id),
            "debug": debug,
            "dry_run" : dryrun,
            }

        res = requests.post(inventory_url, headers=headers,data=json.dumps(body))
        self.logout(token)
        return res.json()


if __name__ == "__main__":
    AnsibleSemaphore.run()
