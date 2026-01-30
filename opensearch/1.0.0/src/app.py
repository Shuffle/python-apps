import ast
import json
import tempfile
import requests

from shuffle_sdk import AppBase


class OpenSearch(AppBase):
    __version__ = "1.0.0"
    app_name = "opensearch"

    def __init__(self, redis, logger, console_logger=None):
        super().__init__(redis, logger, console_logger)

    def _normalize_base_url(self, base_url):
        if not base_url:
            raise ValueError("base_url is required")
        base_url = base_url.strip()
        if not base_url.startswith("http://") and not base_url.startswith("https://"):
            base_url = f"https://{base_url}"
        return base_url.rstrip("/")

    def _to_bool(self, value, default=True):
        if value is None or value == "":
            return default
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in ["true", "1", "yes", "y"]:
            return True
        if text in ["false", "0", "no", "n"]:
            return False
        return default

    def _parse_json_input(self, data):
        if data is None:
            return None
        if isinstance(data, (dict, list)):
            return data
        if isinstance(data, str):
            text = data.strip()
            if text == "":
                return None
            if text.startswith("{") or text.startswith("["):
                try:
                    return json.loads(text)
                except Exception:
                    try:
                        return ast.literal_eval(text)
                    except Exception:
                        return data
            return data
        return data

    def _write_temp_file(self, data, suffix):
        tmp = tempfile.NamedTemporaryFile(delete=False, prefix="shuffle_opensearch_", suffix=suffix)
        tmp.write(data)
        tmp.flush()
        tmp.close()
        return tmp.name

    def _load_file_or_value(self, value, suffix):
        if not value:
            return None
        if isinstance(value, str) and "-----BEGIN" in value:
            return self._write_temp_file(value.encode("utf-8"), suffix)
        filedata = self.get_file(value)
        if not filedata or not filedata.get("success"):
            raise ValueError("Failed to read file from Shuffle")
        return self._write_temp_file(filedata["data"], suffix)

    def _format_response(self, response):
        body = response.text
        try:
            body = response.json()
        except Exception:
            pass
        return {
            "status": response.status_code,
            "body": body,
            "headers": dict(response.headers),
            "url": response.url,
            "success": response.ok,
        }

    def _request(
        self,
        method,
        path,
        base_url,
        client_cert,
        client_key,
        ca_cert=None,
        verify=True,
        headers=None,
        params=None,
        body=None,
        timeout=30,
    ):
        base_url = self._normalize_base_url(base_url)
        url = f"{base_url}{path}"

        cert_path = self._load_file_or_value(client_cert, "_client_cert.pem") if client_cert else None
        key_path = self._load_file_or_value(client_key, "_client_key.pem") if client_key else None
        ca_path = self._load_file_or_value(ca_cert, "_ca_cert.pem") if ca_cert else None

        verify_flag = self._to_bool(verify, True)
        if not verify_flag:
            verify_value = False
        elif ca_path:
            verify_value = ca_path
        else:
            verify_value = True

        cert_value = None
        if cert_path and key_path:
            cert_value = (cert_path, key_path)
        elif cert_path:
            cert_value = cert_path

        if not timeout:
            timeout = 30
        try:
            timeout = int(timeout)
        except Exception:
            timeout = 30

        parsed_body = self._parse_json_input(body)
        request_headers = headers or {}

        request_kwargs = {
            "method": method,
            "url": url,
            "headers": request_headers,
            "params": params,
            "verify": verify_value,
            "timeout": timeout,
        }

        if cert_value:
            request_kwargs["cert"] = cert_value

        if isinstance(parsed_body, (dict, list)):
            request_kwargs["json"] = parsed_body
        elif parsed_body is not None:
            request_kwargs["data"] = parsed_body

        response = requests.request(**request_kwargs)
        return self._format_response(response)

    def cluster_health(self, base_url, client_cert, client_key, ca_cert=None, verify=True, timeout=30):
        return self._request(
            "GET",
            "/_cluster/health",
            base_url,
            client_cert,
            client_key,
            ca_cert=ca_cert,
            verify=verify,
            timeout=timeout,
        )

    def list_indices(self, base_url, client_cert, client_key, ca_cert=None, verify=True, timeout=30):
        params = {"format": "json"}
        return self._request(
            "GET",
            "/_cat/indices",
            base_url,
            client_cert,
            client_key,
            ca_cert=ca_cert,
            verify=verify,
            params=params,
            timeout=timeout,
        )

    def get_index(self, index, base_url, client_cert, client_key, ca_cert=None, verify=True, timeout=30):
        return self._request(
            "GET",
            f"/{index}",
            base_url,
            client_cert,
            client_key,
            ca_cert=ca_cert,
            verify=verify,
            timeout=timeout,
        )

    def create_index(self, index, body, base_url, client_cert, client_key, ca_cert=None, verify=True, timeout=30):
        return self._request(
            "PUT",
            f"/{index}",
            base_url,
            client_cert,
            client_key,
            ca_cert=ca_cert,
            verify=verify,
            body=body,
            timeout=timeout,
        )

    def delete_index(self, index, base_url, client_cert, client_key, ca_cert=None, verify=True, timeout=30):
        return self._request(
            "DELETE",
            f"/{index}",
            base_url,
            client_cert,
            client_key,
            ca_cert=ca_cert,
            verify=verify,
            timeout=timeout,
        )

    def index_document(
        self,
        index,
        document_id,
        body,
        refresh,
        base_url,
        client_cert,
        client_key,
        ca_cert=None,
        verify=True,
        timeout=30,
    ):
        params = {}
        if refresh:
            params["refresh"] = refresh
        return self._request(
            "PUT",
            f"/{index}/_doc/{document_id}",
            base_url,
            client_cert,
            client_key,
            ca_cert=ca_cert,
            verify=verify,
            params=params,
            body=body,
            timeout=timeout,
        )

    def create_document(
        self,
        index,
        body,
        refresh,
        base_url,
        client_cert,
        client_key,
        ca_cert=None,
        verify=True,
        timeout=30,
    ):
        params = {}
        if refresh:
            params["refresh"] = refresh
        return self._request(
            "POST",
            f"/{index}/_doc",
            base_url,
            client_cert,
            client_key,
            ca_cert=ca_cert,
            verify=verify,
            params=params,
            body=body,
            timeout=timeout,
        )

    def get_document(
        self,
        index,
        document_id,
        base_url,
        client_cert,
        client_key,
        ca_cert=None,
        verify=True,
        timeout=30,
    ):
        return self._request(
            "GET",
            f"/{index}/_doc/{document_id}",
            base_url,
            client_cert,
            client_key,
            ca_cert=ca_cert,
            verify=verify,
            timeout=timeout,
        )

    def update_document(
        self,
        index,
        document_id,
        body,
        refresh,
        base_url,
        client_cert,
        client_key,
        ca_cert=None,
        verify=True,
        timeout=30,
    ):
        params = {}
        if refresh:
            params["refresh"] = refresh
        return self._request(
            "POST",
            f"/{index}/_update/{document_id}",
            base_url,
            client_cert,
            client_key,
            ca_cert=ca_cert,
            verify=verify,
            params=params,
            body=body,
            timeout=timeout,
        )

    def delete_document(
        self,
        index,
        document_id,
        refresh,
        base_url,
        client_cert,
        client_key,
        ca_cert=None,
        verify=True,
        timeout=30,
    ):
        params = {}
        if refresh:
            params["refresh"] = refresh
        return self._request(
            "DELETE",
            f"/{index}/_doc/{document_id}",
            base_url,
            client_cert,
            client_key,
            ca_cert=ca_cert,
            verify=verify,
            params=params,
            timeout=timeout,
        )

    def search(
        self,
        index,
        query_body,
        query_string,
        base_url,
        client_cert,
        client_key,
        ca_cert=None,
        verify=True,
        timeout=30,
    ):
        params = {}
        if query_string:
            params["q"] = query_string
        if query_body:
            return self._request(
                "POST",
                f"/{index}/_search",
                base_url,
                client_cert,
                client_key,
                ca_cert=ca_cert,
                verify=verify,
                params=params,
                body=query_body,
                timeout=timeout,
            )
        return self._request(
            "GET",
            f"/{index}/_search",
            base_url,
            client_cert,
            client_key,
            ca_cert=ca_cert,
            verify=verify,
            params=params,
            timeout=timeout,
        )

    def bulk(
        self,
        payload,
        refresh,
        base_url,
        client_cert,
        client_key,
        ca_cert=None,
        verify=True,
        timeout=30,
    ):
        params = {}
        if refresh:
            params["refresh"] = refresh
        headers = {"Content-Type": "application/x-ndjson"}
        return self._request(
            "POST",
            "/_bulk",
            base_url,
            client_cert,
            client_key,
            ca_cert=ca_cert,
            verify=verify,
            params=params,
            body=payload,
            headers=headers,
            timeout=timeout,
        )

    def raw_request(
        self,
        method,
        path,
        body,
        headers,
        params,
        base_url,
        client_cert,
        client_key,
        ca_cert=None,
        verify=True,
        timeout=30,
    ):
        parsed_headers = {}
        parsed_params = {}
        if headers:
            parsed_headers = self._parse_json_input(headers)
            if not isinstance(parsed_headers, dict):
                parsed_headers = {}
        if params:
            parsed_params = self._parse_json_input(params)
            if not isinstance(parsed_params, dict):
                parsed_params = {}
        return self._request(
            method.upper(),
            path,
            base_url,
            client_cert,
            client_key,
            ca_cert=ca_cert,
            verify=verify,
            headers=parsed_headers,
            params=parsed_params,
            body=body,
            timeout=timeout,
        )


if __name__ == "__main__":
    OpenSearch.run()
