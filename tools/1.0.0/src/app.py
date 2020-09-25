import socket
import asyncio
import time
import random
import json
import subprocess

from ioc_finder import find_iocs
from walkoff_app_sdk.app_base import AppBase

class Tools(AppBase):
    """
    An example of a Walkoff App.
    Inherit from the AppBase class to have Redis, logging, and console logging set up behind the scenes.
    """
    __version__ = "1.0.0"
    app_name = "Shuffle Tools"  # this needs to match "name" in api.yaml for WALKOFF to work

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

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
                                    data = {"data": subitem, "data_type": "%s_%s" % (key[:-1], subkey)}
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
                item = item.replace("\'", "\"", -1)
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
        #compile()

        return "Some return: %s" % shuffle_input 

    async def execute_bash(self, code, shuffle_input):
        process = subprocess.Popen(code, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
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
            input_list = input_list.replace("\'", "\"", -1)
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
        input_list = input_list.replace("\'", "\"", -1)
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
                    print("Checking %s vs %s" % (list_item[fieldsplit[index]],  valuesplit[index]))
                    if list_item[fieldsplit[index]] == valuesplit[index]:
                        new_list.append(list_item)

            index += 1

        #"=",
        #"equals",
        #"!=",
        #"does not equal",
        #">",
        #"larger than",
        #"<",
        #"less than",
        #">=",
        #"<=",
        #"startswith",
        #"endswith",
        #"contains",
        #"re",
        #"matches regex",

        try:
            new_list = json.dumps(new_list)
        except json.decoder.JSONDecodeError as e:
            return "Failed parsing filter list output" % e

        return new_list

if __name__ == "__main__":
    asyncio.run(Tools.run(), debug=True)
