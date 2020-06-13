import time
import json
import json
import random
import socket
import asyncio
import requests

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

    # This is a mail function of Shuffle
    async def send_mail_shuffle(self, apikey, recipients, subject, body):
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
        headers={"Authorization": "Bearer %s" % apikey}
        return requests.post(url, headers=headers, json=data).text

    async def send_mail(self, username, password, smtp_host, recipient, subject, body, smtp_port):
        if type(smtp_port) == str:
            try:
                smtp_port = int(smtp_port)
            except ValueError:
                return "SMTP port needs to be a number (Current: %s)" % smtp_port
        
        try:
            s = smtplib.SMTP(host=smtp_host, port=smtp_port)
        except socket.gaierror:
            return "Bad SMTP host or port"
            
        s.starttls()

        try:
            s.login(username, password)
        except smtplib.SMTPAuthenticationError:
            return "Bad username or password"
        
        # setup the parameters of the message
        msg = MIMEMultipart()       
        msg['From']=username
        msg['To']=recipient
        msg['Subject']=subject
        msg.attach(MIMEText(body, 'plain'))
        
        s.send_message(msg)
        print("Successfully sent email with subject %s to %s" % (subject, recipient))
        return "Email sent to %s!" % recipient

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
