import time
import json
import json
import random
import socket
import asyncio
import requests

class Lastline(AppBase):
    __version__ = "1.0.0"
    app_name = "lastline"  

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)
        self.headers = {}

    def login(self, url, user, password):
        url = "%s/papi/login.json"  % url
        data = {
            "username": user,
            "password": password,
        }

        session = requests.Session()
        session.post(url, data=data)
        return session

    def logout(self, url, session):
        url = "%s/papi/logout.json" % url
        
        return session.get(url)

    async def get_event(url, user, password, event_id):
        session = login(url, user, password)
    
        params = {
            "event_id": event_id,
        }
    
        url = "%s/papi/net/event/get.json" % (url)
        ret = session.get(url, params=params)
    
        logout(url, session)
        return ret.text
    
    async def get_mail_attachments(url, user, password, start_time, end_time, limit=1):
        session = login(url, user, password)
    
        params = {
            "start_time": start_time,
            "end_time": end_time,
            "max_results": limit,
        }
    
        url = "%s/papi/net/mail/unique_attachments.json" % (url)
        ret = session.get(url, params=params)
    
        logout(url, session)
        return ret.text
    
    async def get_mail_urls(url, user, password, start_time, end_time, limit=1):
        session = login(url, user, password)
    
        params = {
            "start_time": start_time,
            "end_time": end_time,
            "max_results": limit,
        }
    
        url = "%s/papi/net/mail/unique_urls.json" % (url)
        ret = session.get(url, params=params)
    
        logout(url, session)
        return ret.text
    
    async def get_network_events(url, user, password, start_time, end_time, limit=1, src_ip="", dst_ip="", port="", event_id="", incident_id="", priority=""):
        session = login(url, user, password)
    
        params = {
            "start_time": start_time,
            "end_time": end_time,
            "max_results": limit,
        }
    
        if src_ip:
            params["src_ip"] = src_ip
        if dst_ip:
            params["dst_ip"] = dst_ip 
        if port:
            params["port"] = port
        if event_id:
            params["event_id"] = event_id 
        if incident_id:
            params["incident_id"] = incident_id 
        if priority:
            params["priority"] = priority 
    
        print(params)
    
        url = "%s/papi/net/event/list.json" % (url)
        ret = session.get(url, params=params)
    
        logout(url, session)
        return ret.text
    
    async def get_endpoint_events(url, user, password, start_time, end_time, limit=1, file_md5="", malscape_task_uuid="", ioc_task_uuid=""):
        session = login(url, user, password)
    
        params = {
            "start_time": start_time,
            "end_time": end_time,
            "max_results": limit,
        }
    
        if file_md5:
            params["file_md5"] = file_md5
        if malscape_task_uuid:
            params["malscape_task_uuid"] = malscape_task_uuid
        if ioc_task_uuid:
            params["ioc_task_uuid"] = ioc_task_uuid 
    
        print(params)
    
        url = "%s/papi/net/endpoint/get_alerts.json" % (url)
        ret = session.get(url, params=params)
    
        logout(url, session)
        return ret.text
    
    
    async def get_history(url, user, password, limit=1):
        session = login(url, user, password)
    
        params = {
            "limit": int(limit)
        }
    
        url = "%s/papi/analysis/get_history.json" % (url)
        ret = session.get(url, params=params, headers={})
    
        logout(url, session)
        return ret.text
    
    async def submit_url(url, user, password, url_to_submit):
        session = login(url, user, password)
    
        params = {
            "url": url_to_submit
        }
    
        url = "%s/papi/analysis/submit_url.json" % (url)
        ret = session.post(url, params=params, headers={})
    
        logout(url, session)
        return ret.text

# Run the actual thing after we've checked params
def run(request):
    action = request.get_json() 
    print(action)
    print(type(action))
    authorization_key = action.get("authorization")
    current_execution_id = action.get("execution_id")
	
    if action and "name" in action and "app_name" in action:
        asyncio.run(Lastline.run(action), debug=True)
        return f'Attempting to execute function {action["name"]} in app {action["app_name"]}' 
    else:
        return f'Invalid action'

	
