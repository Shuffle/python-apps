import json
import uuid
import socket
import asyncio
import requests
import tempfile
import datetime
import base64
import imaplib
import smtplib
import time
import random
import eml_parser
import jsonpickle

from glom import glom
from msg_parser import MsOxMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from shuffle_sdk import AppBase 

def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial

def default(o):
    """helpers to store item in json
    arguments:
    - o: field of the object to serialize
    returns:
    - valid serialized value for unserializable fields
    """
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if isinstance(o, set):
        return list(o)
    if isinstance(o, bytes):
        try:
            return o.decode("utf-8")
        except:
            print("Failed parsing utf-8 string")
            return o


class Email(AppBase):
    __version__ = "1.3.0"
    app_name = "email"

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    # This is an email function of Shuffle
    def send_email_shuffle(self, apikey, recipients, subject, body):
        targets = [recipients]
        if ", " in recipients:
            targets = recipients.split(", ")
        elif "," in recipients:
            targets = recipients.split(",")

        newtargets = []
        for target in targets:
            newtarget = target.strip()
            if newtarget: 
                newtargets.append(newtarget)

        targets = newtargets

        data = {
            "targets": targets, 
            "body": body, 
            "subject": subject, 
            "type": "alert", 
            "email_app": True,
            "reference_execution": self.current_execution_id,
        }
        
        url = "https://shuffler.io/functions/sendmail"
        
        if apikey.strip() == "" and self.authorization != "standalone":
            apikey = self.authorization
        
        headers = {"Authorization": "Bearer %s" % apikey}
        return requests.post(url, headers=headers, json=data).text

    def send_email_smtp(self, smtp_host, recipient, subject, body, smtp_port, attachments="", username="", password="", ssl_verify="True", body_type="html", cc_emails=""):
        self.logger.info("Sending email to %s with subject %s" % (recipient, subject))
        if type(smtp_port) == str:
            try:
                smtp_port = int(smtp_port)
            except ValueError:
                return "SMTP port needs to be a number (Current: %s)" % smtp_port

        if "office365.com" in smtp_host:
            return {
                "success": False,
                "reason": "Office 365 does not easily support SMTP anymore, and recommends the Graph API. Please use the Outlook Office365 app in Shuffle with the 'send email' action."
            }

        self.logger.info("Pre SMTP setup")
        try:
            s = smtplib.SMTP(host=smtp_host, port=smtp_port)
        except socket.gaierror as e:
            return f"Bad SMTP host or port: {e}"

        # This is not how it should work.. 
        # Port 465 & 587 = TLS. Sometimes 25.
        if ssl_verify == "false" or ssl_verify == "False":
            pass
        else:
            s.starttls()

        self.logger.info("Pre SMTP auth")
        if len(username) > 1 or len(password) > 1:
            try:
                s.login(username, password)
            except Exception as e:
                if len(password) == 0:
                    self.logger.info("[WARNING] Auth failed (2). No password provided. Continuing as auth may not be necessary.")
                else:
                    return {
                        "success": False,
                        "reason": f"General login exception: {e}"
                    }

            except smtplib.SMTPAuthenticationError as e:
                if len(password) == 0:
                    self.logger.info("[WARNING] Auth failed. No password provided. Continuing as auth may not be necessary.")
                else:
                    return {
                        "success": False,
                        "reason": f"Bad username or password: {e}"
                    }

        if body_type == "" or len(body_type) < 3:
            body_type = "html"

        # setup the parameters of the message
        self.logger.info("Pre mime multipart")
        msg = MIMEMultipart()
        msg["From"] = username
        if len(username) == 0:
            return {
                "success": False,
                "reason": "No username provided (sender). Please provide a username. Required since January 2025."
            }

        msg["To"] = recipient
        msg["Subject"] = subject
        
        if cc_emails: 
            msg["Cc"] = cc_emails
        
        self.logger.info("Pre mime check")
        msg.attach(MIMEText(body, body_type))

        # Read the attachments
        attachment_count = 0
        self.logger.info("Pre attachments")
        try:
            if attachments != None and len(attachments) > 0:
                print("Got attachments: %s" % attachments)
                attachmentsplit = attachments.split(",")

                #attachments = parse_list(attachments, splitter=",")
                #print("Got attachments2: %s" % attachmentsplit)
                print("Before loop")
                files = []
                for file_id in attachmentsplit:
                    print(f"Looping {file_id}")
                    file_id = file_id.strip()
                    new_file = self.get_file(file_id)
                    print(f"New file: {new_file}")
                    try:
                        part = MIMEApplication(
                            new_file["data"],
                            Name=new_file["filename"],
                        )
                        part["Content-Disposition"] = f"attachment; filename=\"{new_file['filename']}\""
                        msg.attach(part)
                        attachment_count += 1
                    except Exception as e:
                        print(f"[WARNING] Failed to attach {file_id}: {e}")


                    #files.append(new_file)

                #return files
                #data["attachments"] = files
        except Exception as e:
            self.logger.info(f"Error in attachment parsing for email: {e}")

        self.logger.info(f"Pre send msg: {msg}")
        try:
            s.send_message(msg)
        except smtplib.SMTPDataError as e: 
            return {
                "success": False,
                "reason": f"Failed to send mail: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "reason": f"Failed to send mail (2): {e}"
            }

        self.logger.info("Successfully sent email with subject %s to %s" % (subject, recipient))
        return {
            "success": True, 
            "reason": "Email sent to %s, %s!" % (recipient, cc_emails) if cc_emails else "Email sent to %s!" % recipient,
            "attachments": attachment_count
        }

    def get_emails_imap(
        self,
        username,
        password,
        imap_server,
        foldername,
        amount,
        unread,
        fields,
        include_raw_body,
        include_attachment_data,
        upload_email_shuffle,
        upload_attachments_shuffle,
        ssl_verify="True",
        mark_as_read="False",
    ):
        def path_to_dict(path, value=None):
            def pack(parts):
                return (
                    {parts[0]: pack(parts[1:]) if len(parts) > 1 else value}
                    if len(parts) > 1
                    else {parts[0]: value}
                )

            return pack(path.split("."))

        def merge(d1, d2):
            for k in d2:
                if k in d1 and isinstance(d1[k], dict) and isinstance(d2[k], dict):
                    merge(d1[k], d2[k])
                else:
                    d1[k] = d2[k]

        #if isinstance(mark_as_read, str):
        #    if str(mark_as_read).lower() == "true":
        #        mark_as_read = True
        #    else:
        #        mark_as_read = False 

        if type(amount) == str:
            try:
                amount = int(amount)
            except ValueError:
                return {
                    "success": False,
                    "reason": "Amount needs to be a number, not %s" % amount,
                }

        try:
            email = imaplib.IMAP4_SSL(imap_server)
        except ConnectionRefusedError as error:
            try:
                email = imaplib.IMAP4(imap_server)

                if ssl_verify == "false" or ssl_verify == "False" or ssl_verify == False:
                    pass
                else:
                    email.starttls()
            except socket.gaierror as error:
                return {
                    "success": False,
                    "reason": "Can't connect to IMAP server %s: %s" % (imap_server, error),
                }
        except socket.gaierror as error:
            return {
                "success": False,
                "reason": "Can't connect to IMAP server %s: %s" % (imap_server, error),
            }

        try:
            email.login(username, password)
        except imaplib.IMAP4.error as error:
            return {
                "success": False,
                "reason": "Failed to log into %s: %s" % (username, error),
            }

        email.select(foldername)
        unread = True if unread.lower().strip() == "true" else False
        
        try:
            # IMAP search queries, e.g. "seen" or "read"
            # https://www.rebex.net/secure-mail.net/features/imap-search.aspx
            mode = "(UNSEEN)" if unread else "ALL"
            thistype, data = email.search(None, mode)
        except imaplib.IMAP4.error as error:
            return {
                "success": False,
                "reason": "Couldn't find folder %s." % (foldername),
            }

        email_ids = data[0]
        id_list = email_ids.split()
        if id_list == None:
            return {
                "success": False,
                "reason": f"Couldn't retrieve email. Data: {data}",
            }

        #try:
        #    self.logger.info(f"LIST: {id_list}")
        #except TypeError:
        #    return {
        #        "success": False,
        #        "reason": "Error getting email. Data: %s" % data,
        #    }

        mark_as_read = True if str(mark_as_read).lower().strip() == "true" else False
        include_raw_body = True if str(include_raw_body).lower().strip() == "true" else False
        include_attachment_data = (
            True if str(include_attachment_data).lower().strip() == "true" else False
        )
        upload_email_shuffle = (
            True if str(upload_email_shuffle).lower().strip() == "true" else False
        )
        upload_attachments_shuffle = (
            True if str(upload_attachments_shuffle).lower().strip() == "true" else False
        )

        # Convert <amount> of mails in json
        emails = []
        ep = eml_parser.EmlParser(
            include_attachment_data=include_attachment_data
            or upload_attachments_shuffle,
            include_raw_body=include_raw_body,
        )

        if len(id_list) == 0:
            return {
                "success": True,
                "messages": [],
            }

        try:
            amount = len(id_list) if len(id_list)<amount else amount 
            for i in range(len(id_list) - 1, len(id_list) - amount - 1, -1):
                resp, data = email.fetch(id_list[i], "(RFC822)")
                error = None

                if resp != "OK":
                    self.logger.info("Failed getting %s" % id_list[i])
                    continue

                if data == None:
                    continue

                if not mark_as_read:
                    email.store(id_list[i], "-FLAGS", '\Seen')

                output_dict = {}
                parsed_eml = ep.decode_email_bytes(data[0][1])

                if fields and fields.strip() != "":
                    for field in fields.split(","):
                        field = field.strip()
                        merge(
                            output_dict,
                            path_to_dict(
                                field,
                                glom(parsed_eml, field, default=None),
                            ),
                        )
                else:
                    output_dict = parsed_eml

                output_dict["imap_id"] = id_list[i]

                # Add message-id as top returned field
                try:
                    output_dict["message_id"] = parsed_eml["header"]["header"]["message-id"][0]
                except Exception as _:
                    output_dict["message_id"] = ""


                if upload_email_shuffle:
                    self.logger.info("Uploading email to shuffle")
                    email_up = [{"filename": "email.msg", "data": data[0][1]}]
                    email_id = self.set_files(email_up)
                    output_dict["email_uid"] = email_id[0]

                if upload_attachments_shuffle:
                    self.logger.info("Uploading email ATTACHMENTS to shuffle")
                    try:
                        atts_up = [{
                                "filename": x["filename"],
                                "data": base64.b64decode(x["raw"]),
                            }
                            for x in parsed_eml["attachment"]
                        ]

                        atts_ids = self.set_files(atts_up)
                        output_dict["attachment_uids"] = atts_ids

                        # Don't need this raw.
                        for x in parsed_eml["attachment"]:
                            x["raw"] = "Removed and saved in the uploaded file"

                    except Exception as e:
                        self.logger.info(f"Major issue with EML attachment - are there attachments: {e}")
                else:
                    output_dict["attachment"] = []
                    output_dict["attachment_uids"] = []
                
                emails.append(output_dict)
        except Exception as err:
            return {
                "success": False,
                "reason": "Error during email processing: {}".format(err),
            }

        try:
            to_return = {
                "success": True,
                "messages": json.loads(json.dumps(emails, default=default)),
            }

            return to_return
        except:
            return {
                "success": True,
                "messages": json.dumps(emails, default=default),
            }

    def remove_similar_items(self, items):
        # Sort items by length in descending order
        items = sorted(items, key=len, reverse=True)
        result = []

        for domain in items:
            # Check if the domain is part of any domain already in the result
            if not any(domain in main for main in result):
                result.append(domain)
        
        return result

    def parse_eml(self, filedata, extract_attachments=False):
        if filedata.startswith("file_"):
            return self.parse_email_file(filedata, extract_attachments)

        parsedfile = {
            "success": True,
            "filename": "email.eml",
            "data": filedata,
        }

        # Encode the data as utf-8 if it's not base64
        if not str(parsedfile["data"]).endswith("="):
            parsedfile["data"] = parsedfile["data"].encode("utf-8")

        return self.parse_email_file(parsedfile, extract_attachments)

    def parse_email_file(self, file_id, extract_attachments=False):
        file_path = {
            "success": False,
        }

        if isinstance(file_id, dict) and "data" in file_id:
            file_path = file_id
        else:
            file_path = self.get_file(file_id)

        if file_path["success"] == False:
            return {
                "success": False,
                "reason": "Couldn't get file with ID %s" % file_id
            }

        # Check if data is in base64 and decode it
        # If it ends with = then it may be bas64

        if str(file_path["data"]).endswith("="):
            try:
                file_path["data"] = base64.b64decode(file_path["data"])
            except Exception as e:
                print(f"Failed to decode base64: {e}")

        #print("POST: ", file_path)

        #print("File: %s" % file_path)
        print('working with .eml file? %s' % file_path["filename"])

        if extract_attachments == "true":
            extract_attachments = True
        else:
            extract_attachments = False

        # Replace raw newlines \\r\\n with actual newlines
        # The data is a byte string, so we need to decode it to utf-8
        try:
            #print("Pre size: %d" % len(file_path["data"]))
            file_path["data"] = file_path["data"].decode("utf-8").replace("\\r\\n", "\n").encode("utf-8")
            #print("Post size: %d" % len(file_path["data"]))
        except Exception as e:
            print(f"Failed to decode file: {e}")
            pass

        # Makes msg into eml
        if ".msg" in file_path["filename"] or "." not in file_path["filename"]:
            self.logger.info(f"[DEBUG] Working with .msg file {file_path['filename']}. Filesize: {len(file_path['data'])}")
            try:
                result = {}
                msg = MsOxMessage(file_path['data'])

                emldata = msg.get_email_mime_content()
                file_path["data"] = emldata.encode()

            except Exception as e:
                if ".msg" in file_path["filename"]:
                    return {"success":False, "reason":f"Exception occured during msg parsing: {e}"}    


        ep = eml_parser.EmlParser(
            include_attachment_data=True, 
            include_raw_body=True 
        )

        try:
            self.logger.info("Pre email")
            parsed_eml = ep.decode_email_bytes(file_path['data'])
            #if str(parsed_eml["header"]["date"]) == "1970-01-01 00:00:00+00:00" and len(parsed_eml["header"]["subject"]) == 0:
            #    return {"success":False,"reason":"Not a valid EML/MSG file, or the file have a timestamp or subject defined (required).", "date": str(parsed_eml["header"]["date"]), "subject": str(parsed_eml["header"]["subject"])}

            # Put attachments in the shuffle file system
            self.logger.info("Pre attachment")
            if extract_attachments == True and "attachment" in parsed_eml:
                cnt = -1 

                self.logger.info("[INFO] Uploading %d attachments" % len(parsed_eml["attachment"]))
                for value in parsed_eml["attachment"]:
                    cnt += 1
                    if value["raw"] == None:
                        parsed_eml["attachment"][cnt]["file_id"] = "Not available"
                        continue

                    file = {
                        "filename": value["filename"],
                        "data": base64.b64decode(value["raw"]),
                    }

                    file_id = self.set_files([file])
                    if len(file_id) == 0:
                        parsed_eml["attachment"][cnt]["file_id"] = "File upload failed"
                    else:
                        parsed_eml["attachment"][cnt]["file_id"] = file_id[0]

            if not "attachment" in parsed_eml:
                parsed_eml["attachment"] = []

            self.logger.info("Post attachment. Has body: %s" % ("body" in parsed_eml))

            try:
                if "body" in parsed_eml and len(parsed_eml["body"]) > 0:

                    for i in range(len(parsed_eml["body"])):
                        if "uri" in parsed_eml["body"][i] and len(parsed_eml["body"][i]["uri"]) > 0:
                            parsed_eml["body"][i]["uri"] = self.remove_similar_items(parsed_eml["body"][i]["uri"])

                        if "email" in parsed_eml["body"][i] and len(parsed_eml["body"][i]["email"]) > 0:
                            parsed_eml["body"][i]["email"] = self.remove_similar_items(parsed_eml["body"][i]["email"])

                        if "domain" in parsed_eml["body"][i] and len(parsed_eml["body"][i]["domain"]) > 0:
                            parsed_eml["body"][i]["domain"] = self.remove_similar_items(parsed_eml["body"][i]["domain"])

            except Exception as e:
                self.logger.info(f"[ERROR] Failed to remove similar items: {e}")

            parsed_eml["success"] = True
            return json.dumps(parsed_eml, default=json_serial)   
        except Exception as e:
            return {"success":False, "reason": f"An exception occured during EML parsing: {e}. Please contact support"} 
    
        return {"success": False, "reason": "No email has been defined for this file type"}
               

    def parse_email_headers(self, email_headers):
        try:
            email_headers = bytes(email_headers,'utf-8')
            ep = eml_parser.EmlParser()
            parsed_headers = ep.decode_email_bytes(email_headers)
            return json.dumps(parsed_headers, default=json_serial)   
        except Exception as e:
            raise Exception(e)

    # Basic function to check headers in an email
    # Can be dumped in in pretty much any format
    def analyze_headers(self, headers):
        self.logger.info("Input headers: %s" % headers)

        # Raw
        if isinstance(headers, str):
            headers = self.parse_email_headers(headers)
            if isinstance(headers, str):
                headers = json.loads(headers)
    
            headers = headers["header"]["header"]
    
        # Just a way to parse out shitty email formats 
        if "header" in headers:
            headers = headers["header"]
            if "header" in headers:
                headers = headers["header"]

        if "headers" in headers:
            headers = headers["headers"]
            if "headers" in headers:
                headers = headers["headers"]
        
        if not isinstance(headers, list):
            newheaders = []
            for key, value in headers.items():
                if isinstance(value, list):
                    newheaders.append({
                        "key": key,
                        "value": value[0],
                    })
                else:
                    newheaders.append({
                        "key": key,
                        "value": value,
                    })
    
            headers = newheaders

        #self.logger.info("Parsed headers: %s" % headers)
    
        spf = False
        dkim = False
        dmarc = False
        spoofed = False

        analyzed_headers = {
            "success": True,
            "sender": "",
            "receiver": "",
            "subject": "",
            "date": "",
            "details": {
                "spf": "",
                "dkim": "",
                "dmarc": "",
                "spoofed": "",
            },
        }

        for item in headers:
            if "name" in item:
                item["key"] = item["name"]
    
            item["key"] = item["key"].lower()

            # Handle sender/receiver
            if item["key"] == "from" or item["key"] == "sender" or item["key"] == "delivered-to":
                analyzed_headers["sender"] = item["value"]

            if item["key"] == "to" or item["key"] == "receiver" or item["key"] == "delivered-to":
                analyzed_headers["receiver"] = item["value"]

            if item["key"] == "subject" or item["key"] == "title":
                analyzed_headers["subject"] = item["value"]

            if item["key"] == "date": 
                analyzed_headers["date"] = item["value"]
    
            if "spf" in item["key"]:
                analyzed_headers["details"]["spf"] = spf
                if "pass " in item["value"].lower():
                    spf = True
    
            if "dkim" in item["key"]:
                analyzed_headers["details"]["dkim"] = dkim
                if "pass " in item["value"].lower():
                    dkim = True
    
            if "dmarc" in item["key"]:
                analyzed_headers["details"]["dmarc"] = dmarc
                print("dmarc: ", item["key"])
    
            if item["key"].lower() == "authentication-results":
                if "spf" in item["value"].lower():
                    analyzed_headers["details"]["spf"] = spf

                if "dkim" in item["value"].lower():
                    analyzed_headers["details"]["dkim"] = dkim

                if "dmarc" in item["value"].lower():
                    analyzed_headers["details"]["dmarc"] = dmarc

                if "spf=pass" in item["value"]:
                    spf = True
                if "dkim=pass" in item["value"]:
                    dkim = True
                if "dmarc=pass" in item["value"]:
                    dmarc = True
    
            # Fix spoofed!
            if item["key"] == "from":
                print("From: " + item["value"])

                if "<" in item["value"]:
                    item["value"] = item["value"].split("<")[1]

                for subitem in headers:
                    if "name" in subitem:
                        subitem["key"] = subitem["name"]

                    subitem["key"] = subitem["key"].lower()
    
                    if subitem["key"] == "reply-to":

                        if "<" in subitem["value"]:
                            subitem["value"] = subitem["value"].split("<")[1]

                        if item["value"] != subitem["value"]:
                            spoofed = True
                            analyzed_headers["spoofed_reason"] = "Reply-To is different than From"
                            analyzed_headers["details"]["spoofed"] = subitem["value"]
                            break


                    if subitem["key"] == "mail-reply-to":
                        print("Reply-To: " + subitem["value"], item["value"])

                        if "<" in subitem["value"]:
                            subitem["value"] = subitem["value"].split("<")[1]

                        if item["value"] != subitem["value"]:
                            spoofed = True
                            analyzed_headers["spoofed_reason"] = "Mail-Reply-To is different than From"
                            analyzed_headers["details"]["spoofed"] = subitem["value"]
                            break

        analyzed_headers["spf"] = spf
        analyzed_headers["dkim"] = dkim
        analyzed_headers["dmarc"] = dmarc
        analyzed_headers["spoofed"] = spoofed
    
        # Should be a dictionary
        return analyzed_headers 

    # This is an SMS function of Shuffle
    def send_sms_shuffle(self, apikey, phone_numbers, body):
        phone_numbers = phone_numbers.replace(" ", "")
        targets = phone_numbers.split(",")

        data = {"numbers": targets, "body": body}

        url = "https://shuffler.io/api/v1/functions/sendsms"
        headers = {"Authorization": "Bearer %s" % apikey}
        return requests.post(url, headers=headers, json=data, verify=False).text


# Run the actual thing after we've checked params
def run(request):
    action = request.get_json()
    authorization_key = action.get("authorization")
    current_execution_id = action.get("execution_id")

    if action and "name" in action and "app_name" in action:
        Email.run(action)
        return f'Attempting to execute function {action["name"]} in app {action["app_name"]}'
    else:
        return f"Invalid action"


if __name__ == "__main__":
    Email.run()
