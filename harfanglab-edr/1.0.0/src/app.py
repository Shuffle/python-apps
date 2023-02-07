import socket
import asyncio
import time
import random
import json
from datetime import datetime, timedelta, timezone
import requests
import dateutil.parser
from harfanglab_sdk import *

from walkoff_app_sdk.app_base import AppBase


class HarfangLabEDR(AppBase):
    __version__ = "1.0.0"
    app_name = "HarfangLab EDR"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    def fetch_incidents(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, first_fetch = None, alert_status = None, alert_type = None, min_severity = None, max_fetch = None, only_new_alerts = None, delay = 0, exclude_rules = None):
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)
        try:

            excluded_rules = None

            last_fetch = None

            if only_new_alerts == 'true':
                last_fetch = self.get_cache('last_fetch').get('value', None)

            if exclude_rules:
                excluded_rules = exclude_rules.lower().split('\n')

            (latest_created_time_us, events) = conn.fetch_security_events(first_fetch, alert_status, alert_type, min_severity, max_fetch, last_fetch, delay, excluded_rules)

            if only_new_alerts == 'true':
                self.set_cache('last_fetch', latest_created_time_us)

            return events

        except Exception as e:
            raise Exception(f'Failed to fetch incidents: {str(e)}')


    def add_ioc_to_source(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, ioc_value, ioc_type, ioc_comment, ioc_status, source_name):
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)
        try:
            return conn.add_ioc_to_source(ioc_value, ioc_type, ioc_comment, ioc_status, source_name)
        except Exception as e:
            return f'Failed to add IOC {ioc_value} to source {source_name}: %s' % (str(e))

    def change_security_event_status(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, event_id, status):
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)
        try:
            return conn.change_security_event_status(event_id, status)
        except Exception as e:
            return f'Failed to change the status of the security incident: %s' % (str(e))

    def isolate_endpoint(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, agent_id):
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)
        try:
            self.logger.debug(f'verify: {conn.verify}')
            return conn.isolate_endpoint(agent_id)
        except Exception as e:
            return f'Failed to isolate endpoint: %s' % (str(e))

    def unisolate_endpoint(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, agent_id):
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)
        try:
            return conn.unisolate_endpoint(agent_id)
        except Exception as e:
            return f'Failed to unisolate endpoint: %s' % (str(e))

    def run_job(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, job_name, agent_id, job_title, job_description, job_timeout):
        if not job_timeout or job_timeout == '':
            job_timeout = '600'
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)

        try:
            return conn.run_job(job_name, agent_id, job_title, job_description, int(job_timeout))
        except Exception as e:
            return f'Failed to run job: %s' % (str(e))

    def dump_process(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, agent_id, process_uuid, job_timeout):
        if not job_timeout or job_timeout == '':
            job_timeout = '600'
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)

        try:
            return conn.dump_process(agent_id, process_uuid, int(job_timeout))
        except Exception as e:
            return f'Failed to dump process: %s' % (str(e))

    def kill_process(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, agent_id, process_uuid, job_timeout):
        if not job_timeout or job_timeout == '':
            job_timeout = '600'
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)

        try:
            return conn.kill_process(agent_id, process_uuid, int(job_timeout))
        except Exception as e:
            return f'Failed to kill process: %s' % (str(e))


    def telemetry_search_hash(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, hash, process_name, image_name, limit):
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)
        if not limit or limit == '':
            limit = None
        else:
            limit = int(limit)

        args = {
            'hash': hash,
            'process_name': process_name,
            'image_name': image_name,
            'limit': limit
        }
        try:
            return conn.search_telemetry('searchHash', args)
        except Exception as e:
            return f'Failed to search in telemetry: %s' % (str(e))

    def telemetry_search_driver_by_hash(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, hash, limit):
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)
        if not limit or limit == '':
            limit = None
        else:
            limit = int(limit)

        args = {
            'hash': hash,
            'limit': limit
        }
        try:
            return conn.search_telemetry('searchDriverByHash', args)
        except Exception as e:
            return f'Failed to search in telemetry: %s' % (str(e))

    def telemetry_search_driver_by_filename(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, filename, limit):
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)
        if not limit or limit == '':
            limit = None
        else:
            limit = int(limit)

        args = {
            'filename': filename,
            'limit': limit
        }
        try:
            return conn.search_telemetry('searchDriverByFileName', args)
        except Exception as e:
            return f'Failed to search in telemetry: %s' % (str(e))

    def telemetry_search_destination_ip(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, ip, limit):
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)
        if not limit or limit == '':
            limit = None
        else:
            limit = int(limit)

        args = {
            'ip': ip,
            'limit': limit
        }
        try:
            return conn.search_telemetry('searchDestinationIP', args)
        except Exception as e:
            return f'Failed to search in telemetry: %s' % (str(e))

    def telemetry_search_source_ip(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, ip, limit):
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)
        if not limit or limit == '':
            limit = None
        else:
            limit = int(limit)

        args = {
            'ip': ip,
            'limit': limit
        }
        try:
            return conn.search_telemetry('searchSourceIP', args)
        except Exception as e:
            return f'Failed to search in telemetry: %s' % (str(e))

    def telemetry_get_binary(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, hash):
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)

        args = {
            'hash': hash
        }
        try:
            return conn.search_telemetry('getBinary', args)
        except Exception as e:
            return f'Failed to search in telemetry: %s' % (str(e))

    def telemetry_search_iocs(self, base_url, api_key, verify_certificate, http_proxy, https_proxy, iocs, limit, search_types):
        conn = HarfangLabConnector(base_url, api_key, verify_certificate, http_proxy, https_proxy, self.logger)
        if not limit or limit == '':
            limit = None
        else:
            limit = int(limit)

        iocs_json = json.loads(iocs)
        search_types_array = search_types.split(',')
        try:
            return conn.search_multiple_iocs_in_telemetry(iocs_json, limit, search_types_array)
        except Exception as e:
            return f'Failed to search IOCs in telemetry: %s' % (str(e))


if __name__ == "__main__":
    HarfangLabEDR.run()
