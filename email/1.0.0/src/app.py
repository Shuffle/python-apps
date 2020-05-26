import time
import json
import json
import random
import socket
import asyncio
import requests

from walkoff_app_sdk.app_base import AppBase

class Email(AppBase):
    __version__ = "1.0.0"
    app_name = "email"  

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    async def send_mail(self, recipients, subject, body):
        targets = [recipients]
        if ", " in recipients:
            targets = recipients.split(", ")
        elif "," in recipients:
            targets = recipients.split(",")

        data = {
            "targets": targets,
            "body": body,
            "subject": subject,
            "type": "alert",
        }

        url = "https://shuffler.io/functions/sendmail"
        key = "377469e8-dd5d-4521-8d9e-416d8d2f6fd5"
        headers={"Authorization": "Bearer %s" % key}
        return requests.post(url, headers=headers, json=data).text

# Run the actual thing after we've checked params
def run(request):
    action = request.get_json() 
    print(action)
    print(type(action))
    authorization_key = action.get("authorization")
    current_execution_id = action.get("execution_id")
	
    if action and "name" in action and "app_name" in action:
        asyncio.run(Email.run(action), debug=True)
        return f'Attempting to execute function {action["name"]} in app {action["app_name"]}' 
    else:
        return f'Invalid action'

if __name__ == "__main__":
    asyncio.run(Email.run(), debug=True)
