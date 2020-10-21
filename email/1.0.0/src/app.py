import time
import json
import random
import socket
import asyncio
import requests

import imaplib
import smtplib
import eml_parser
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

    async def get_mail_imap(self, username, password, imap_server, foldername, amount):
        if type(amount) == str:
            try:
                amount = int(amount)
            except ValueError:
                return "Amount needs to be a number, not %s" % amount

        try:
            mail = imaplib.IMAP4_SSL(imap_server)
        except socket.gaierror as error:
            try:
                mail = imaplib.IMAP4(imap_server)
                mail.starttls()
            except socket.gaierror as error:
                return "Can't connect to IMAP server %s: %s" % (imap_server, error)
    
        try:
            mail.login(username, password)
        except imaplib.IMAP4.error as error:
            return "Failed to log into %s: %s" % (username, error)
    
        mail.select(foldername)
        try:
            # IMAP search queries, e.g. "seen" or "read"
            # https://www.rebex.net/secure-mail.net/features/imap-search.aspx
            thistype, data = mail.search(None, 'ALL')
        except imaplib.IMAP4.error as error:
            return "Couldn't find folder %s." % (foldername)
    
        mail_ids = data[0]
        id_list = mail_ids.split()
        if id_list == None:
            return "Couldn't retrieve mail. Data: %s" % data
    
        try:
            print("LIST: ", len(id_list))
        except TypeError:
            return "Error getting mail. Data: %s" % data
        
        # FIXME: Should parse as JSON.
        emails = []
        
        ep = eml_parser.EmlParser()

        for i in range(len(id_list)-1, len(id_list)-amount, -1):
            resp, data = mail.fetch(id_list[i], "(RFC822)")
            if resp != 'OK':
                print("Failed getting %s" % id_list[i])
                continue
    
            if data == None:
                continue

            try:
                parsed_eml = ep.decode_email_bytes(data[0][1])

            except UnicodeDecodeError as err:
                print("Failed to decode part of mail %s" % id_list[i])
                data = "Failed to decode mail %s" % id_list[i]
            except IndexError as err:
                print("Indexerror: %s" % err)
                data = "Something went wrong while parsing. Check logs."

            emails.append({"id": id_list[i].decode("utf-8"), "data": parsed_eml})

        return json.dumps(emails)

# Run the actual thing after we've checked params
def run(request):
    action = request.get_json() 
    authorization_key = action.get("authorization")
    current_execution_id = action.get("execution_id")
	
    if action and "name" in action and "app_name" in action:
        asyncio.run(Email.run(action), debug=True)
        return f'Attempting to execute function {action["name"]} in app {action["app_name"]}' 
    else:
        return f'Invalid action'

if __name__ == "__main__":
    asyncio.run(Email.run(), debug=True)
