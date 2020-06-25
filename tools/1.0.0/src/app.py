import socket
import asyncio
import time
import random
import json

from ioc_finder import find_iocs
from walkoff_app_sdk.app_base import AppBase

class Tools(AppBase):
    """
    An example of a Walkoff App.
    Inherit from the AppBase class to have Redis, logging, and console logging set up behind the scenes.
    """
    __version__ = "1.0.0"
    app_name = "hello_world"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    async def parse_ioc(self, input_string):
        iocs = find_iocs(input_string)
        newarray = []
        for key, value in iocs.items():
            if len(value) > 0:
                for item in value:
                    # If in here: attack techniques. Shouldn't be 3 levels so no
                    # recursion necessary
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if len(subvalue) > 0:
                                for subitem in subvalue:
                                    data = {"data": subitem, "data_type": "%s_%s" % (key, subkey)}
                                    if data not in newarray:
                                        newarray.append(data)
                    else:
                        data = {"data": item, "data_type": key}
                        if data not in newarray:
                            newarray.append(data)

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

if __name__ == "__main__":
    asyncio.run(Tools.run(), debug=True)
