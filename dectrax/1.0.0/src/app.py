#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
import json

try:
    from walkoff_app_sdk.app_base import AppBase
except ImportError:
    try:
        from shuffle_sdk import AppBase
    except ImportError:
        # Fallback for local testing, CI pipelines, and standalone execution
        class AppBase:
            def __init__(self, redis=None, logger=None, console_logger=None):
                self.redis = redis
                self.logger = logger
                self.console_logger = console_logger

            @classmethod
            def run(cls):
                print(f"Running {cls.__name__} in standalone mode")


class DECTRAX(AppBase):
    """
    DECTRAX Shuffle SOAR App
    Enables autonomous cyber deception, honeytoken provisioning, and line-rate firewall interdiction.
    """
    __version__ = "1.0.0"
    app_name = "dectrax"

    def __init__(self, redis=None, logger=None, console_logger=None):
        super().__init__(redis, logger, console_logger)

    def block_ip(self, apikey, ip, reason="Shuffle SOAR Automated Interdiction", base_url="https://api.dectrax.com"):
        """
        Publishes a confirmed adversary IP into DECTRAX's live External Dynamic List (EDL) feed
        for automated perimeter/internal firewall drops in <1.5s.
        """
        clean_base = base_url.rstrip("/")
        headers = {
            "Authorization": f"Bearer {apikey}",
            "Content-Type": "application/json",
            "User-Agent": "DECTRAX-Shuffle-SOAR/1.0"
        }
        payload = {
            "ip": ip.strip(),
            "reason": reason
        }
        try:
            res = requests.post(
                f"{clean_base}/api/v1/edl/block",
                json=payload,
                headers=headers,
                timeout=10
            )
            if res.status_code == 200:
                try:
                    return res.json()
                except ValueError:
                    return {"status": "success", "message": res.text, "ip": ip}
            else:
                return {
                    "status": "error",
                    "code": res.status_code,
                    "message": res.text
                }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Network exception communicating with DECTRAX: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_blocked_ips(self, apikey, base_url="https://api.dectrax.com"):
        """
        Retrieves the current active firewall blocklist consumed by Palo Alto, Fortinet, and nftables.
        """
        clean_base = base_url.rstrip("/")
        headers = {
            "Authorization": f"Bearer {apikey}",
            "User-Agent": "DECTRAX-Shuffle-SOAR/1.0"
        }
        try:
            res = requests.get(
                f"{clean_base}/api/v1/edl/firewall.txt",
                headers=headers,
                timeout=10
            )
            if res.status_code == 200:
                ips = [line.strip() for line in res.text.splitlines() if line.strip() and not line.startswith("#")]
                return {
                    "status": "success",
                    "count": len(ips),
                    "blocked_ips": ips
                }
            else:
                return {
                    "status": "error",
                    "code": res.status_code,
                    "message": res.text
                }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Network exception communicating with DECTRAX: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_recent_threats(self, apikey, limit=50, base_url="https://api.dectrax.com"):
        """
        Fetches high-fidelity deception breach events and attacker TTPs with 0.00% false positive accuracy.
        """
        clean_base = base_url.rstrip("/")
        headers = {
            "Authorization": f"Bearer {apikey}",
            "User-Agent": "DECTRAX-Shuffle-SOAR/1.0"
        }
        params = {"limit": int(limit)}
        try:
            res = requests.get(
                f"{clean_base}/api/attacks/recent",
                headers=headers,
                params=params,
                timeout=10
            )
            if res.status_code == 200:
                try:
                    data = res.json()
                    return data
                except ValueError:
                    return {"status": "success", "raw": res.text}
            else:
                return {
                    "status": "error",
                    "code": res.status_code,
                    "message": res.text
                }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Network exception communicating with DECTRAX: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_honeytoken(self, apikey, token_type="aws_key", memo="Shuffle Automated Deployment", base_url="https://api.dectrax.com"):
        """
        Provisions synthetic canary tokens (AWS access keys, database credentials, JWTs, Kerberos SPNs)
        to seed across high-value servers, GitHub repositories, or Active Directory.
        """
        clean_base = base_url.rstrip("/")
        headers = {
            "Authorization": f"Bearer {apikey}",
            "Content-Type": "application/json",
            "User-Agent": "DECTRAX-Shuffle-SOAR/1.0"
        }
        payload = {
            "token_type": token_type,
            "memo": memo
        }
        try:
            res = requests.post(
                f"{clean_base}/api/v1/canary/generate",
                json=payload,
                headers=headers,
                timeout=10
            )
            if res.status_code == 200:
                try:
                    return res.json()
                except ValueError:
                    return {"status": "success", "raw": res.text}
            else:
                return {
                    "status": "error",
                    "code": res.status_code,
                    "message": res.text
                }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Network exception communicating with DECTRAX: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    DECTRAX.run()
