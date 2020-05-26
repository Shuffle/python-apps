import time
import json
import random
import socket
import asyncio
import requests

from walkoff_app_sdk.app_base import AppBase

class Servicenow(AppBase):
    __version__ = "1.0.0"
    app_name = "servicenow"  

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    def send_request(self, url, username, password, path, method='get', body=None, params=None, headers=None, file=None):
        body = body if body is not None else {}
        params = params if params is not None else {}
    
        url = '{}{}'.format(url, path)
        print(url)
        if not headers:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        if file:
            # Not supported in v2
            url = url.replace('v2', 'v1')
            try:
                file_entry = file['id']
                file_name = file['name']
                shutil.copy(demisto.getFilePath(file_entry)['path'], file_name)
                with open(file_name, 'rb') as f:
                    files = {'file': f}
                    try:
                        res = requests.request(method, url, headers=headers, params=params, data=body, files=files, auth=(username, password))
                    except requests.exceptions.ReadTimeout as e:
                        return "Readtimeout: %s" % e
                    except requests.exceptions.ConnectionError as e:
                        return "ConnectionError: %s" % e
                shutil.rmtree(demisto.getFilePath(file_entry)['name'], ignore_errors=True)
            except Exception as e:
                return 'Failed to upload file - ' + str(e)
        else:
            try:
                print((username, password))
                res = requests.request(method, url, headers=headers, data=json.dumps(body) if body else {}, params=params, auth=(username, password))
            except requests.exceptions.ReadTimeout as e:
                return "Readtimeout: %s" % e
            except requests.exceptions.ConnectionError as e:
                return "ConnectionError: %s" % e
    
        try:
            obj = res.json()
        except Exception as e:
            if not res.content:
                return ''
            return 'Error parsing reply - {} - {}'.format(res.content, str(e))
    
        if 'error' in obj:
            message = obj.get('error', {}).get('message')
            details = obj.get('error', {}).get('detail')
            if message == 'No Record found':
                return {
                    # Return an empty results array
                    'result': []
                }
            return 'ServiceNow Error: {}, details: {}'.format(message, details)
    
        if res.status_code < 200 or res.status_code >= 300:
            return 'Got status code {} with url {} with body {} with headers {}'.format(str(res.status_code), url, str(res.content), str(res.headers))
    
        return obj.text
    
    async def get_ticket(self, url, username, password, table_name, record_id, number=None):
        path = None
        query_params = {}  # type: Dict
        if record_id:
            path = 'table/' + table_name + '/' + record_id
        elif number:
            path = 'table/' + table_name
            query_params = {
                'number': number
            }
        else:
            # Only in cases where the table is of type ticket
            return 'servicenow-get-ticket requires either ticket ID or ticket number'
    
        return self.send_request(url, username, password, path, 'get', params=query_params)
    
    async def get_table(self, url, username, password, table_name, limit=1):
        query_params = {
            "sysparm_limit": limit,     
        }  
    
        path = 'table/%s' % table_name 
        return send_request(self, url, username, password, path, 'get', params=query_params)

# Run the actual thing after we've checked params
def run(request):
    action = request.get_json() 
    print(action)
    print(type(action))
    authorization_key = action.get("authorization")
    current_execution_id = action.get("execution_id")
	
    if action and "name" in action and "app_name" in action:
        asyncio.run(Servicenow.run(action), debug=True)
        return f'Attempting to execute function {action["name"]} in app {action["app_name"]}' 
    else:
        return f'Invalid action'

	
