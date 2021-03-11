import socket
import asyncio
import time
import random
import json
import requests

from walkoff_app_sdk.app_base import AppBase

class Pagerduty(AppBase):
    __version__ = "1.0.0"
    app_name = "PagerDuty"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    async def list_all_incidents(self, api_key):
        url = 'https://api.pagerduty.com/incidents'
        headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=api_key)
        }
        try:
            r = requests.get(url, headers=headers)
            return json.dumps(r.json())
        except Exception as e:
            return e.__class__

    async def get_incident_details(self, api_key, incident_id):
        url = f'https://api.pagerduty.com/incidents/{incident_id}'
        headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': f'Token token={api_key}'
        }
        try:
            r = requests.get(url, headers=headers)
            return json.dumps(r.json())
        except Exception as e:
            return e.__class__        
    
    async def create_incident(self, api_key, email, title, service_id, urgency, details):
        url = 'https://api.pagerduty.com/incidents/'
        headers = {
            'Accept': 'application/vnd.pagerduty+json;version=2',
            'Authorization': f'Token token={api_key}',
            'Content-type': 'application/json',
            'From': str(email)
        }

        payload =  {
            "incident": {
                "type": "incident",
                "title": title,
                "service": {
                    "id": service_id,
                    "type": "service_reference"
                },
                "urgency": urgency,
                "body": {
                    "type": "incident_body",
                    "details": details
                }
            }
        }

        try:
            r = requests.post(url, headers=headers, data=json.dumps(payload))
            return json.dumps(r.json())
        except Exception as e:
            return e.__class__  

    async def get_past_incidents(self, api_key, incident_id):
        url = f'https://api.pagerduty.com/incidents/{incident_id}/past_incidents'
        
        headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': f'Token token={api_key}'
        }
        try:
            r = requests.get(url, headers = headers)
            return r.json()
        except Exception as e:
            return e.__class__

    async def update_incident_status(self, api_key, email, incident_id, status):
        url = f'https://api.pagerduty.com/incidents/{incident_id}'
        
        headers = {
            'Accept': 'application/vnd.pagerduty+json;version=2',
            'Authorization': f'Token token={api_key}',
            'Content-type': 'application/json',
            'From': str(email)
        }

        payload = {
            'incident':{
            'type': 'incident',
            'status': status
            }
        }

        try:
            r = requests.put(url, headers=headers, data=json.dumps(payload))
            return r.json()
        except Exception as e:
            return e.__class__

    async def create_incident_note(self, api_key, email, incident_id, content):
        url = f'https://api.pagerduty.com/incidents/{incident_id}/notes'

        headers = {
            'Accept': 'application/vnd.pagerduty+json;version=2',
            'Authorization': f'Token token={api_key}',
            'Content-type': 'application/json',
            'From': str(email)
        }

        payload = {
            'note': {
                    'content': content
                }
        }
        try:
            r = requests.post(url, headers=headers, data=json.dumps(payload))
            return r.json()
        except Exception as e:
            return e.__class__    


if __name__ == "__main__":
    asyncio.run(Pagerduty.run(), debug=True)
