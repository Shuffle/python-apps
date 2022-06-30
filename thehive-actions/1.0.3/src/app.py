import socket
import asyncio
import time
import random
import json
import requests
import thehive4py

from thehive4py.api import TheHiveApi
from thehive4py.query import *
import thehive4py.models
from thehive4py.models import CaseHelper, CaseTask, CaseObservable

from walkoff_app_sdk.app_base import AppBase


class TheHiveActions(AppBase):
    __version__ = "1.0.3"
    app_name = "TheHive Actions"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    def run_responder(self, url, apikey, case_id, responder_id):
        self.logger.info("--- Running run_responder ---")
        request_url = f"{url}/api/connector/cortex/action"
        headers = {"Authorization": "Bearer %s" % apikey}
        payload = {
            "responderId": responder_id,
            "objectType": "case",
            "objectId": case_id
        }
        try:
            r = requests.post(request_url, data=payload, headers=headers)
            r_json = r.json()
            message = {
                "status_code": r.status_code,
                "response": r.json()
            }
            if r.status_code == 200:
                return json.dumps(message)
            else:
                raise Exception(message)
        except Exception as e:
            self.logger.info(f"Failure : {e}")
            return e

    def run_responder_from_list(self, url, apikey, case_id, responder):
        self.logger.info("--- Running run_responder ---")
        request_url = f"{url}/api/connector/cortex/action"
        headers = {"Authorization": "Bearer %s" % apikey}
        if responder == "PrismaCloud_GetAlertStatus":
            responder_id = "68d6c37ffbfbf7a541ad8ee1a1aed443"
        elif responder == "PrismaCloud_RemediateAlert":
            responder_id = "7229b7ce6b4ebf2e6b277eba5fc96d9f"
        elif responder == "SMAX_GetIncidentInfos":
            responder_id = "a10200991085a2a25d91e886b582a6fd"
        else:
            return {"success": False, "reason": "No responder provided"}
        payload = {
            "responderId": responder_id,
            "objectType": "case",
            "objectId": case_id
        }
        r = requests.post(request_url, data=payload, headers=headers)
        r_json = r.json()
        success = True
        if r.status_code != 200:
            success = False
        message = {
            "success": success,
            "status_code": r.status_code,
            "response": r.json()
        }
        return message

    def get_observable_from_case_id(self, case_id, dataType, url, apikey):
        self.logger.info("--- Running get_observable_from_case_id ---")
        api = TheHiveApi(url, apikey)
        try:
            case_observables = api.get_case_observables(case_id).json()
            output_filter = [
                x for x in case_observables if x['dataType'] == dataType]
        except Exception as e:
            self.logger.info(f"Failure : {e}")
        if output_filter == []:
            error_message = "Error : Observable " + dataType + " not found!"
            raise IOError(error_message)
        # Retrieving observable value position
        else:
            observable_value = output_filter[0]["data"]
            self.logger.info("For " + dataType +
                             ", observable value is : " + observable_value)
            return observable_value

    def import_alert(self, alert_id, url, apikey):
        self.logger.info("--- Running import_alert ---")
        api = TheHiveApi(url, apikey)
        self.logger.info('Promoting alert %s to a case' % alert_id)
        self.logger.info('-----------------------------')
        try:
            response = api.promote_alert_to_case(alert_id)
            if response.status_code == 201:
                data = response.json()
                self.logger.info("Case ID created : " + data["_id"])
                interpretation = "Alert was successfully imported or was already imported"
                created_case_id = data["_id"]
            else:
                data = response.json()
                interpretation = "Dont kno"
                created_case_id = None
            message = {
                "status_code": response.status_code,
                "data": response.json(),
                "message": interpretation,
                "imported_alert": alert_id,
                "created_case_id": created_case_id}
            return json.dumps(message)
        except Exception as e:
            self.logger.info(f"Failure : {e}")
            return e.__class__

    def close_case(self, case_id, url, apikey, resolution_status, impact_status, summary, tags="",
                   tags_mode="append"):
        self.logger.info(f'Closing case {case_id} in TheHive...')

        if tags:
            if ", " in tags:
                tags = tags.split(", ")
            elif "," in tags:
                tags = tags.split(",")
            else:
                tags = [tags]
        else:
            tags = []

        if not url.startswith("http"):
            url = f"http://{url}"

        api = TheHiveApi(url, apikey)
        case_helper = CaseHelper(api)

        case_kwargs = {"status": "Resolved",
                       "resolutionStatus": resolution_status,
                       "impactStatus": impact_status,
                       "summary": summary}

        if tags is not None:
            if tags_mode == "append":
                tags = case_helper(case_id).tags + tags
            case_kwargs["tags"] = tags

        return case_helper.update(case_id, **case_kwargs).jsonify()

    def update_case(self, case_id, payload, url, apikey):
        url = url + "/api/case/" + str(case_id)
        headers = {
            "Authorization": "Bearer " + str(apikey)
        }
        # payload = json.loads(payload)

        try:
            success = True
            r = requests.patch(url, headers=headers, json=payload)
            if r.status_code != 200:
                success = False
            message = {
                "success": success,
                "status_code": r.status_code,
                "data": r.json(),
                "payload": payload
            }
            return message
        except Exception as e:
            self.logger.info(f"Failure : {e}")
            return e

    def get_case(self, case_id, url, apikey):
        url = url + "/api/case/" + str(case_id)
        headers = {
            "Authorization": "Bearer " + str(apikey)
        }
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                return r.json()
            else:
                raise Exception("something went wrong... " +
                                str(r.text) + " status code : " + str(r.status_code))
        except Exception as e:
            self.logger.info(f"Failure : (e)")
            return e

    def get_tasks(self, case_id, url, apikey):
        url = url + "/api/v0/query"
        headers = {
            "Authorization": "Bearer " + str(apikey)
        }
        payload = {
            "query": [
                {
                    "_name": "getCase",
                    "idOrName": str(case_id)
                },
                {
                    "_name": "tasks"
                }
                # },
                # {
                #     "_name": "filter",
                #     "status": "InProgress"
                # }
            ]
        }
        try:
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code == 200:
                return r.json()
            else:
                raise Exception("something went wrong... " +
                                str(r.text) + " status code : " + str(r.status_code))
        except Exception as e:
            self.logger.info(f"Failure : (e)")
            return e

    # def get_taskss(self, case_id, url, apikey):
    #     url = url + "/api/v0/query"
    #     headers = {
    #         "Authorization": "Bearer " + str(apikey)
    #     }
    #     payload = {
    #         "query": [
    #             {
    #                 "_name": "getCase",
    #                 "idOrName": str(case_id)
    #             },
    #             {
    #                 "_name": "tasks"
    #             }
    #         ]
    #     }
    #     try:
    #         r = requests.post(url, headers=headers, json=payload)
    #         if r.status_code == 200:
    #             return r.json()
    #         else:
    #             raise Exception("something went wrong... " +
    #                             str(r.text) + " status code : " + str(r.status_code))
    #     except Exception as e:
    #         self.logger.info(f"Failure : (e)")
    #         return e


if __name__ == "__main__":
    TheHiveActions.run()
