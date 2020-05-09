#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import time
import random
import requests
import urllib3

from walkoff_app_sdk.app_base import AppBase

class Splunk(AppBase):
    """
    Splunk integration for WALKOFF with some basic features
    """
    __version__ = "1.0.0"
    app_name = "splunk"

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        self.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        super().__init__(redis, logger, console_logger)

    async def echo(self, input_data):
        return input_data 

    def run_search(self, auth, url, query):
        url = '%s/services/search/jobs?output_mode=json' % (url)
        ret = requests.post(url, auth=auth, data=query, timeout=timeout, verify=False)
        return ret

    def get_search(self, auth, url, search_sid):
        # Wait for search to be done?
        url = '%s/services/search/jobs/%s?output_mode=json' % (url, search_sid)

        time.sleep(0.2)
        maxrunduration = 30
        ret = ""
        while(True):
            try:
                ret = requests.get(url, auth=auth, timeout=timeout, verify=False)
            except requests.exceptions.ConnectionError:
                time.sleep(1)
                continue

            try:
                content = ret.json()["entry"][0]["content"]
            except KeyError as e:
                print("\nKEYERROR: %s\n" % content)
                time.sleep(1)
                continue

            try:
                if content["resultCount"] > 0 or content["isDone"] or content["isFinalized"] or content["runDuration"] > maxrunduration:
                    print(content)
                    break
            except KeyError:
                try:
                	print(ret.json()["messages"])
                except KeyError:
                    print(content)
                
            time.sleep(1)

        return ret

    async def SplunkQuery(self, url, username, password, query, result_limit=100, earliest_time="-24h", latest_time="now"):
        auth = (username, password)

        # "latest_time": "now"
        query = {
            "search": "| search %s" % query,
            "exec_mode": "normal",
            "count": result_limit,
            "earliest_time": earliest_time,
            "latest_time": latest_time
        }

        print("Current search: %s" % query["search"])

        try:
            ret = self.run_search(auth, url, query)
        except requests.exceptions.ConnectTimeout as e:
            print("Timeout: %s" % e)
            return "0"

        if ret.status_code != 201:
            print("Bad status code: %d" % ret.status_code)
            return "0"

        search_id = ret.json()["sid"]

        print("Search ID: %s" % search_id)

        ret = self.get_search(auth, url, search_id)
        if len(ret.json()["entry"]) == 1:
            count = ret.json()["entry"][0]["content"]["resultCount"]
            print("Result: %d" % count)
            return str(count)

        print("No results (or wrong?): %d" % (len(ret.json()["entry"])))
        return "0"
        
if __name__ == "__main__":
    asyncio.run(Splunk.run(), debug=True)
