import time
import json
import random
import socket
import asyncio
import requests
from pyotrs import Article, Client, Ticket, DynamicField, Attachment

class OTRS(AppBase):
    __version__ = "1.0.0"
    app_name = "http"  

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

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
    

# Run the actual thing after we've checked params
def run(request):
    action = request.get_json() 
    print(action)
    print(type(action))
    authorization_key = action.get("authorization")
    current_execution_id = action.get("execution_id")
	
    if action and "name" in action and "app_name" in action:
        asyncio.run(OTRS.run(action), debug=True)
        return f'Attempting to execute function {action["name"]} in app {action["app_name"]}' 
    else:
        return f'Invalid action'

	
