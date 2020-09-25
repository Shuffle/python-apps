#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import time
import random

import requests
import thehive4py
from thehive4py.api import TheHiveApi
from thehive4py.query import *
import thehive4py.models

from walkoff_app_sdk.app_base import AppBase

class TheHive(AppBase):
    """
    An example of a Walkoff App.
    Inherit from the AppBase class to have Redis, logging, and console logging set up behind the scenes.
    """
    __version__ = "1.0.0"
    app_name = "thehive"

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    #async def run_analyzer(self, apikey, url, title_query):
    #    self.thehive = TheHiveApi(url, apikey)

    #    response = self.thehive.find_cases(query=String("title:'%s'" % title_query), range='all', sort=[])
    #    return response.text


    async def search_cases(self, apikey, url, title_query):
        self.thehive = TheHiveApi(url, apikey)

        response = self.thehive.find_cases(query=String("title:'%s'" % title_query), range='all', sort=[])
        return response.text

    async def add_observable(self, apikey, url, case_id, data, datatype, tags):
        self.thehive = TheHiveApi(url, apikey)

        if tags:
            if ", " in tags:
                tags = tags.split(", ")
            elif "," in tags:
                tags = tags.split(",")
            else:
                tags = []
        else:
            tags = []

        item = thehive4py.models.CaseObservable(
            dataType=datatype,
            data=data,
            tlp=1,
            ioc=False,
            sighted=False,
            tags=["Shuffle"],
            message="Created by shuffle",
        )

        return self.thehive.create_case_observable(case_id, item).text

    async def search_alerts(self, apikey, url, title_query):
        self.thehive = TheHiveApi(url, apikey)

        response = self.thehive.find_alerts(query=String("title:'%s'" % title_query), range='all', sort=[])
        return response.text

    async def create_case(self, apikey, url, title, description="", tlp=1, severity=1, tags=""):
        self.thehive = TheHiveApi(url, apikey)
        if tags:
            if ", " in tags:
                tags = tags.split(", ")
            elif "," in tags:
                tags = tags.split(",")
            else:
                tags = []
        else:
            tags = []

        # Wutface fix
        if not tlp:
            tlp = 1
        if not severity:
            severity = 1

        if isinstance(tlp, str):
            if not tlp.isdigit():
                return "TLP needs to be a number from 0-2, not %s" % tlp
            tlp = int(tlp)
        if isinstance(severity, str):
            if not severity.isdigit():
                return "Severity needs to be a number from 0-2, not %s" % tlp

            severity = int(severity)

        if tlp > 3 or tlp < 0:
            return "TLP needs to be a number from 0-3, not %d" % tlp
        if severity > 2 or severity < 0:
            return "Severity needs to be a number from 0-2, not %d" % tlp

        case = thehive4py.models.Case(
            title=title,
            tlp=tlp,
            severity=severity,
            tags=tags,
            description=description,
        )

        try:
            ret = self.thehive.create_case(case)
            return ret.text
        except requests.exceptions.ConnectionError as e:
            return "ConnectionError: %s" % e

    async def create_alert(self, apikey, url, type, source, sourceref, title, description="", tlp=1, severity=1, tags=""):
        self.thehive = TheHiveApi(url, apikey)
        if tags:
            if ", " in tags:
                tags = tags.split(", ")
            elif "," in tags:
                tags = tags.split(",")
            else:
                tags = []
        else:
            tags = []

        # Wutface fix
        if not tlp:
            tlp = 1
        if not severity:
            severity = 1

        if isinstance(tlp, str):
            if not tlp.isdigit():
                return "TLP needs to be a number from 0-2, not %s" % tlp
            tlp = int(tlp)
        if isinstance(severity, str):
            if not severity.isdigit():
                return "Severity needs to be a number from 0-2, not %s" % tlp

            severity = int(severity)

        if tlp > 2 or tlp < 0:
            return "TLP needs to be a number from 0-2, not %d" % tlp
        if severity > 2 or severity < 0:
            return "Severity needs to be a number from 0-2, not %d" % tlp

        alert = thehive4py.models.Alert(
            title=title,
            tlp=tlp,
            severity=severity,
            tags=tags,
            description=description,
            type=type,
            source=source,
            sourceRef=sourceref,
        )

        try:
            ret = self.thehive.create_alert(alert)
            return ret.text
        except requests.exceptions.ConnectionError as e:
            return "ConnectionError: %s" % e

    # Gets an item based on input. E.g. field_type = Alert
    async def get_item(self, apikey, url, field_type, cur_id): 
        self.thehive = TheHiveApi(url, apikey)

        newstr = ""
        ret = ""
        if field_type.lower() == "alert":
            ret = self.thehive.get_alert(cur_id + "?similarity=1") 
        elif field_type.lower() == "case":
            ret = self.thehive.get_case(cur_id)
        elif field_type.lower() == "case_observables":
            ret = self.thehive.get_case_observables(cur_id)
        elif field_type.lower() == "case_task":
            ret = self.thehive.get_case_task(cur_id)
        elif field_type.lower() == "case_tasks":
            ret = self.thehive.get_case_tasks(cur_id)
        elif field_type.lower() == "case_template":
            ret = self.thehive.get_case_tasks(cur_id)
        elif field_type.lower() == "linked_cases":
            ret = self.thehive.get_linked_cases(cur_id)
        elif field_type.lower() == "task_log":
            ret = self.thehive.get_task_log(cur_id)
        elif field_type.lower() == "task_logs":
            ret = self.thehive.get_task_logs(cur_id)
        else:
            return "%s is not implemented. See https://github.com/frikky/shuffle-apps for more info." % field_type

        return ret.text

    async def close_alert(self, apikey, url, alert_id):
        self.thehive = TheHiveApi(url, apikey)
        return self.thehive.mark_alert_as_read(alert_id).text

    async def reopen_alert(self, apikey, url, alert_id):
        self.thehive = TheHiveApi(url, apikey)
        return self.thehive.mark_alert_as_unread(alert_id).text

    async def create_case_from_alert(self, apikey, url, alert_id, case_template=None):
        self.thehive = TheHiveApi(url, apikey)
        response = self.thehive.promote_alert_to_case(alert_id=alert_id, case_template=case_template)
        return response.text

    async def merge_alert_into_case(self, apikey, url, alert_id, case_id):
        self.thehive = TheHiveApi(url, apikey)
        req = url + f"/api/alert/{alert_id}/merge/{case_id}"
        ret = requests.post(req, auth=self.thehive.auth)
        return ret.text

    # Not sure what the data should be
    async def update_field(self, apikey, url, field_type, cur_id, field, data):
        # This is kinda silly but..
        if field_type.lower() == "alert":
            newdata = {}

            if data.startswith("%s"): 
                ticket = self.thehive.get_alert(cur_id)
                if ticket.status_code != 200:
                    pass 
            
                newdata[field] = "%s%s" % (ticket.json()[field], data[2:])
            else:
                newdata[field] = data

            # Bleh
            url = "%s/api/alert/%s" % (url, cur_id)
            if field == "status":
                if data == "New" or data == "Updated":
                    url = "%s/markAsUnread" % url
                elif data == "Ignored": 
                    url = "%s/markAsRead" % url

                ret = requests.post(
                    url,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer %s' % apikey
                    }
                )
            else:
                ret = requests.patch(
                    url,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer %s' % apikey
                    }, 
                    json=newdata,
                )

            return str(ret.status_code)
        else:
            return "%s is not implemented. See https://github.com/frikky/walkoff-integrations for more info." % field_type

    # https://github.com/TheHive-Project/TheHiveDocs/tree/master/api/connectors/cortex
    async def run_analyzer(self, apikey, url, cortex_id, analyzer_id, artifact_id):
        self.thehive = TheHiveApi(url, apikey)
        return self.thehive.run_analyzer(cortex_id, artifact_id, analyzer_id).text

if __name__ == "__main__":
    asyncio.run(TheHive.run(), debug=True)
