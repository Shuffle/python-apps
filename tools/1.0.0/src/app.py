import os
import shutil
import zipfile
import socket
import asyncio
import time
import random
import json
import subprocess
import requests
import tempfile

from ioc_finder import find_iocs
from walkoff_app_sdk.app_base import AppBase


class Tools(AppBase):
    """
    An example of a Walkoff App.
    Inherit from the AppBase class to have Redis, logging, and console logging set up behind the scenes.
    """

    __version__ = "1.0.0"
    app_name = (
        "Shuffle Tools"  # this needs to match "name" in api.yaml for WALKOFF to work
    )

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    # This is an SMS function of Shuffle
    async def send_sms_shuffle(self, apikey, phone_numbers, body):
        targets = [phone_numbers]
        if ", " in phone_numbers:
            targets = phone_numbers.split(", ")
        elif "," in phone_numbers:
            targets = phone_numbers.split(",")

        data = {"numbers": targets, "body": body}

        url = "https://shuffler.io/api/v1/functions/sendsms"
        headers = {"Authorization": "Bearer %s" % apikey}
        return requests.post(url, headers=headers, json=data).text

    # This is an email function of Shuffle
    async def send_email_shuffle(self, apikey, recipients, subject, body):
        targets = [recipients]
        if ", " in recipients:
            targets = recipients.split(", ")
        elif "," in recipients:
            targets = recipients.split(",")

        data = {"targets": targets, "body": body, "subject": subject, "type": "alert"}

        url = "https://shuffler.io/api/v1/functions/sendmail"
        headers = {"Authorization": "Bearer %s" % apikey}
        return requests.post(url, headers=headers, json=data).text

    # https://github.com/fhightower/ioc-finder
    async def parse_ioc(self, input_string, input_type="all"):
        if input_type == "":
            input_type = "all"

        iocs = find_iocs(input_string)
        newarray = []
        for key, value in iocs.items():
            if input_type != "all":
                if key != input_type:
                    continue

            if len(value) > 0:
                for item in value:
                    # If in here: attack techniques. Shouldn't be 3 levels so no
                    # recursion necessary
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if len(subvalue) > 0:
                                for subitem in subvalue:
                                    data = {
                                        "data": subitem,
                                        "data_type": "%s_%s" % (key[:-1], subkey),
                                    }
                                    if data not in newarray:
                                        newarray.append(data)
                    else:
                        data = {"data": item, "data_type": key[:-1]}
                        if data not in newarray:
                            newarray.append(data)

        # Reformatting IP
        for item in newarray:
            if "ip" in item["data_type"]:
                item["data_type"] = "ip"

        try:
            newarray = json.dumps(newarray)
        except json.decoder.JSONDecodeError as e:
            return "Failed to parse IOC's: %s" % e

        return newarray

    async def parse_list(self, items, splitter="\n"):
        if splitter == "":
            splitter = "\n"

        splititems = items.split(splitter)

        return str(splititems)

    async def get_length(self, item):
        if item.startswith("[") and item.endswith("]"):
            try:
                item = item.replace("'", '"', -1)
                item = json.loads(item)
            except json.decoder.JSONDecodeError as e:
                print("Parse error: %s" % e)
                pass

        return str(len(item))

    async def translate_value(self, input_data, translate_from, translate_to):
        splitdata = [translate_from]
        splitvalue = ""
        if ", " in translate_from:
            splitdata = translate_from.split(", ")
        elif "," in translate_from:
            splitdata = translate_from.split(",")

        for item in splitdata:
            input_data = input_data.replace(item, translate_to)

        return input_data

    async def execute_python(self, code, shuffle_input):
        print("Run with shuffle_data %s" % shuffle_input)
        print("And python code %s" % code)
        # Write the code to a file, then jdjd
        exec(code)

        # 1. Take the data into a file
        # 2. Subprocess execute file?

        # May be necessary
        # compile()

        return "Some return: %s" % shuffle_input

    async def execute_bash(self, code, shuffle_input):
        process = subprocess.Popen(
            code, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True
        )
        stdout = process.communicate()
        item = ""
        if len(stdout[0]) > 0:
            print("Succesfully ran bash!")
            item = stdout[0]
        else:
            print("FAILED to run bash!")
            item = stdout[1]

        try:
            ret = item.decode("utf-8")
            return ret
        except:
            return item

        return item

    async def filter_list(self, input_list, field, check, value):
        print("Running function with list %s", input_list)

        try:
            input_list = input_list.replace("'", '"', -1)
            input_list = json.loads(input_list)
        except Exception as e:
            print("Error parsing string to array. Continuing anyway.")

        new_list = []
        try:
            for item in input_list:
                try:
                    item = json.loads(item)
                except:
                    pass

                if check == "equals":
                    if str(item[field]) == value:
                        print("APPENDED BECAUSE %s %s %s" % (field, check, value))
                        new_list.append(item)
                elif check == "does not equal":
                    if str(item[field]) != value:
                        new_list.append(item)
        except Exception as e:
            return "Error: %s" % e

        try:
            new_list = json.dumps(new_list)
        except json.decoder.JSONDecodeError as e:
            return "Failed parsing filter list output: %s" % e

        return new_list

    async def multi_list_filter(self, input_list, field, check, value):
        input_list = input_list.replace("'", '"', -1)
        input_list = json.loads(input_list)

        fieldsplit = field.split(",")
        if ", " in field:
            fieldsplit = field.split(", ")

        valuesplit = value.split(",")
        if ", " in value:
            valuesplit = value.split(", ")

        checksplit = check.split(",")
        if ", " in check:
            checksplit = check.split(", ")

        new_list = []
        for list_item in input_list:
            list_item = json.loads(list_item)

            index = 0
            for check in checksplit:
                if check == "equals":
                    print(
                        "Checking %s vs %s"
                        % (list_item[fieldsplit[index]], valuesplit[index])
                    )
                    if list_item[fieldsplit[index]] == valuesplit[index]:
                        new_list.append(list_item)

            index += 1

        # "=",
        # "equals",
        # "!=",
        # "does not equal",
        # ">",
        # "larger than",
        # "<",
        # "less than",
        # ">=",
        # "<=",
        # "startswith",
        # "endswith",
        # "contains",
        # "re",
        # "matches regex",

        try:
            new_list = json.dumps(new_list)
        except json.decoder.JSONDecodeError as e:
            return "Failed parsing filter list output" % e

        return new_list

    # Use data from AppBase to talk to backend
    async def delete_file(self, file_id):
        headers = {
            "Authorization": "Bearer %s" % self.authorization,
        }
        print("HEADERS: %s" % headers)

        ret = requests.delete(
            "%s/api/v1/files/%s?execution_id=%s"
            % (self.url, file_id, self.current_execution_id),
            headers=headers,
        )
        return ret.text

    async def extract_archive(self, filedata={}, fileformat="zip", password=None):
        uuids = []

        #data = (b"%s" % filedata["data"]).encode("utf-8")
        data = filedata["data"]
        #.encode("utf8")
        #encode("ISO-8859-1")

        try:
            if filedata["success"] == False:
                return "No file to upload. Skipping message."

            print("Working with fileformat %s" % fileformat)
            with tempfile.TemporaryDirectory() as tmpdirname:
                # Get archive and save phisically
                with open(os.path.join(tmpdirname, "archive"), "wb") as f:
                    f.write(data)

                # Extract
                if fileformat.strip().lower() == "zip":
                    with zipfile.ZipFile(
                        os.path.join(tmpdirname, "archive")
                    ) as zip_file:
                        for member in zip_file.namelist():
                            filename = os.path.basename(member)
                            if not filename:
                                continue

                            # get item, push to shuffle, keep uid
                            source = zip_file.open(member)
                            filedata = {
                                "filename": source.name,
                                "data": source.read(),
                            }
                            uuids.append(filedata)
                elif fileformat.strip().lower() == "rar":
                    return "wip"
                elif fileformat.strip().lower() == "7zip":
                    return "wip"
                else:
                    return "No such format: %s" % fileformat
        except Exception as excp:
            print("*" * 100)
            print("Exception: %s" % excp)
            print("*" * 100)
            return "Failure during extract: %s" % excp

        print("Files: %s", uuids)
        return ("Successfully extracted your archive as %s" % fileformat, uuids)

    async def inflate_archive(self, file_uids, fileformat, name, password=None):

        ## TODO: password support
        ## TODO: support rar/7zip

        file_uids = file_uids.split()
        print("picking {}".format(file_uids))
        headers = {
            "Authorization": "Bearer %s" % self.authorization,
        }

        items = []

        for file_id in file_uids:
            ret = requests.get(
                "%s/api/v1/files/%s?execution_id=%s"
                % (self.url, file_id, self.current_execution_id),
                headers=headers,
            )

            if ret.status_code != 200:
                return "Error managing file: [{}] - {}".format(file_id, ret.text)

            filename = ret.json()["filename"]
            ret = requests.get(
                "%s/api/v1/files/%s/content?execution_id=%s"
                % (self.url, file_id, self.current_execution_id),
                headers=headers,
            )

            if ret.status_code != 200:
                return "Error managing file download: [{}] - {}".format(file_id, ret.text)

            data = ret.text
            items.append((filename, data))

        if len(items) == 0:
            return "No file to inflate"

        print("{} items to inflate".format(len(items)))

        if fileformat == "zip":
            archive_name = "archive.zip" if not name else name

            print("Before zip")

            with tempfile.NamedTemporaryFile() as tmp:
                with zipfile.ZipFile(tmp.name, "w", zipfile.ZIP_DEFLATED) as archive:
                    for filename, filedata in items:
                        archive.writestr(filename, filedata)

                data = {
                    "filename": archive_name,
                    "workflow_id": self.full_execution["workflow"]["id"],
                    "org_id": self.full_execution["workflow"]["execution_org"]["id"],
                }

                # Creates an upload location
                ret = requests.post(
                    "%s/api/v1/files/create?execution_id=%s"
                    % (self.url, self.current_execution_id),
                    headers=headers,
                    json=data,
                )

                if ret.status_code != 200:
                    return "Error managing file: {}".format(ret.text)

                # Does the actual upload
                files={"shuffle_file": open(tmp.name, "rb")}
                ret2 = requests.post(
                    "%s/api/v1/files/%s/upload?execution_id=%s" 
                    % (self.url, ret.json()["id"], self.current_execution_id),
                    headers=headers,
                    files=files,
                )

                if ret2.status_code != 200:
                    return "Failed uploading file: {}".format(ret2.text)

                # Returns the first file's ID
                return ret.json()
        else:
            return "wip"


if __name__ == "__main__":
    asyncio.run(Tools.run(), debug=True)
