import json
import base64
import requests
from walkoff_app_sdk.app_base import AppBase


class isMalicious(AppBase):
    __version__ = "1.0.0"
    app_name = "ismalicious"

    def __init__(self, redis, logger, console_logger=None):
        super().__init__(redis, logger, console_logger)

    def _get_auth_header(self, api_key, api_secret):
        """Generate authentication header."""
        credentials = f"{api_key}:{api_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"X-API-KEY": encoded, "Accept": "application/json"}

    def _get_base_url(self, api_url=None):
        """Get base URL with fallback to default."""
        if api_url and api_url.strip():
            return api_url.rstrip("/")
        return "https://ismalicious.com"

    def check_ip(self, api_key, api_secret, ip, enrichment="standard", api_url=None):
        """Check if an IP address is malicious."""
        base_url = self._get_base_url(api_url)
        headers = self._get_auth_header(api_key, api_secret)

        try:
            response = requests.get(
                f"{base_url}/api/check",
                params={"query": ip, "enrichment": enrichment or "standard"},
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            return json.dumps({"success": True, **result})
        except requests.exceptions.RequestException as e:
            return json.dumps({"success": False, "error": str(e)})

    def check_domain(
        self, api_key, api_secret, domain, enrichment="standard", api_url=None
    ):
        """Check if a domain is malicious."""
        base_url = self._get_base_url(api_url)
        headers = self._get_auth_header(api_key, api_secret)

        try:
            response = requests.get(
                f"{base_url}/api/check",
                params={"query": domain, "enrichment": enrichment or "standard"},
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            return json.dumps({"success": True, **result})
        except requests.exceptions.RequestException as e:
            return json.dumps({"success": False, "error": str(e)})

    def get_reputation(self, api_key, api_secret, query, api_url=None):
        """Get reputation data for an IP or domain."""
        base_url = self._get_base_url(api_url)
        headers = self._get_auth_header(api_key, api_secret)

        try:
            response = requests.get(
                f"{base_url}/api/check/reputation",
                params={"query": query},
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            return json.dumps({"success": True, **result})
        except requests.exceptions.RequestException as e:
            return json.dumps({"success": False, "error": str(e)})

    def get_location(self, api_key, api_secret, ip, api_url=None):
        """Get geolocation data for an IP address."""
        base_url = self._get_base_url(api_url)
        headers = self._get_auth_header(api_key, api_secret)

        try:
            response = requests.get(
                f"{base_url}/api/check/location",
                params={"query": ip},
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            return json.dumps({"success": True, **result})
        except requests.exceptions.RequestException as e:
            return json.dumps({"success": False, "error": str(e)})

    def get_blocklist_stats(self, api_key, api_secret, api_url=None):
        """Get statistics about available blocklists."""
        base_url = self._get_base_url(api_url)
        headers = self._get_auth_header(api_key, api_secret)

        try:
            response = requests.get(
                f"{base_url}/api/blocklist/stats",
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            return json.dumps({"success": True, **result})
        except requests.exceptions.RequestException as e:
            return json.dumps({"success": False, "error": str(e)})


if __name__ == "__main__":
    isMalicious.run()
