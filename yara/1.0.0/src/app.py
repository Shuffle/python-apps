import socket
import asyncio
import time
import random
import json
import requests
import yara
import os

from walkoff_app_sdk.app_base import AppBase

class Yara(AppBase):
    __version__ = "1.0.0"
    app_name = "yara"  

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    # Write your data inside this function
    #https://yara.readthedocs.io/en/latest/yarapython.html
    async def analyze_by_rule(self, file_id, rule, timeout=15):
        if timeout == 0 or not timeout:
            timeout = 15
        else:
            timeout = int(timeout)

        print("Getting file: %s" % file_id)
        file_ret = self.get_file(file_id)
        print("FINISHED GETTING FILE: %s" % file_ret)
        #rules.match(file)

        all_matches = []

        rule='rule dummy { condition: true }'
        rules = yara.compile(sources={
            'rule': rule,
        })

        matches = rules.match(data=file_ret["data"], timeout=timeout)
        if len(matches) > 0:
            for item in matches:
                submatch = {
                    "rule": item.rule,
                    "tags": item.tags,
                    "match": item.strings,
                }

                all_matches.append(submatch)

        print("Matches: %d" % len(all_matches))

        try:
            return json.dumps(all_matches)
        except json.JSONDecodeError:
            return all_matches

    # Write your data inside this function
    #https://yara.readthedocs.io/en/latest/yarapython.html
    async def analyze_file(self, file_id, timeout=15):
        if timeout == 0 or not timeout:
            timeout = 15
        else:
            timeout = int(timeout)
        
        print("Getting file: %s" % file_id)
        file_ret = self.get_file(file_id)
        print("FINISHED GETTING FILE: %s" % file_ret)
        #rules.match(file)

        all_matches = []

        basefolder = "/rules"
        filepaths = os.listdir(basefolder)
        print(f"FILES: {filepaths}")
        #filepaths = ["/rules/test_rule", "/rules/eicar.yara"]

        for filepath in filepaths:
            try:
                rules = yara.compile(filepath)
            except:
                print("[INFO] Rule %s failed" % filepath)
                continue

            matches = rules.match(data=file_ret["data"], timeout=timeout)
            if len(matches) > 0:
                for item in matches:
                    submatch = {
                        "rule": item.rule,
                        "tags": item.tags,
                        "match": item.strings,
                    }

                    all_matches.append(submatch)

        print("Matches: %d" % len(all_matches))

        try:
            return json.dumps(all_matches)
        except json.JSONDecodeError:
            return all_matches

if __name__ == "__main__":
    asyncio.run(Yara.run(), debug=True)
