import json
import requests

from shuffle_sdk import AppBase


class Flowtriq(AppBase):
    __version__ = "1.0.0"
    app_name = "Flowtriq"

    def __init__(self, redis, logger, console_logger=None):
        super().__init__(redis, logger, console_logger)

    def _get_verify(self, verify_ssl):
        if not verify_ssl:
            return True
        return str(verify_ssl).lower().strip() != "false"

    def _get_headers(self, api_key):
        return {
            "Authorization": "Bearer %s" % api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _build_url(self, base_url, path):
        base = base_url.rstrip("/")
        return "%s%s" % (base, path)

    def _handle_response(self, response):
        try:
            data = response.json()
        except Exception:
            data = response.text

        result = {
            "success": 200 <= response.status_code < 300,
            "status_code": response.status_code,
        }

        if isinstance(data, dict):
            result.update(data)
        else:
            result["body"] = data

        return json.dumps(result)

    def list_incidents(self, base_url, api_key, verify_ssl="true", status=""):
        url = self._build_url(base_url, "/api/v1/incidents")
        headers = self._get_headers(api_key)
        verify = self._get_verify(verify_ssl)

        params = {}
        if status:
            params["status"] = status

        response = requests.get(url, headers=headers, params=params, verify=verify)
        return self._handle_response(response)

    def get_incident(self, base_url, api_key, incident_id, verify_ssl="true"):
        url = self._build_url(base_url, "/api/v1/incidents/%s" % incident_id)
        headers = self._get_headers(api_key)
        verify = self._get_verify(verify_ssl)

        response = requests.get(url, headers=headers, verify=verify)
        return self._handle_response(response)

    def list_nodes(self, base_url, api_key, verify_ssl="true"):
        url = self._build_url(base_url, "/api/v1/nodes")
        headers = self._get_headers(api_key)
        verify = self._get_verify(verify_ssl)

        response = requests.get(url, headers=headers, verify=verify)
        return self._handle_response(response)

    def create_mitigation_rule(self, base_url, api_key, name, rule_type, target,
                               verify_ssl="true", source_ips="", duration_minutes=""):
        url = self._build_url(base_url, "/api/v1/mitigation/rules")
        headers = self._get_headers(api_key)
        verify = self._get_verify(verify_ssl)

        data = {
            "name": name,
            "rule_type": rule_type,
            "target": target,
        }

        if source_ips:
            ips = [ip.strip() for ip in source_ips.split(",") if ip.strip()]
            if ips:
                data["source_ips"] = ips

        if duration_minutes:
            try:
                data["duration_minutes"] = int(duration_minutes)
            except ValueError:
                pass

        response = requests.post(url, headers=headers, json=data, verify=verify)
        return self._handle_response(response)


def run(request):
    action = request.get_json()
    authorization_key = action.get("authorization")
    current_execution_id = action.get("execution_id")

    if action and "name" in action and "app_name" in action:
        Flowtriq.run(action)
        return 'Attempting to execute function %s in app %s' % (action["name"], action["app_name"])
    else:
        return 'Invalid action'


if __name__ == "__main__":
    Flowtriq.run()
