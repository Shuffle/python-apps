# DECTRAX Shuffle SOAR App

Official open-source integration app for [Shuffle SOAR](https://shuffler.io) to automate active cyber deception, canary honeytoken provisioning, and line-rate firewall containment with **DECTRAX**.

[![App Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](api.yaml)
[![License](https://img.shields.io/badge/license-Apache--2.0-yellow.svg)](https://www.apache.org/licenses/LICENSE-2.0.html)
[![Category](https://img.shields.io/badge/category-Deception%20%7C%20Incident%20Response-red.svg)](https://dectrax.com)

---

## Overview

DECTRAX delivers enterprise cyber deception with **0.00% false positive fidelity** and **sub-1.5 second automated firewall interdiction**. 

Unlike conventional SIEM correlation rules that burden analysts with ambiguous alerts and 45+ minute triage queues, DECTRAX operates synthetic decoy assets (LDAP, RDP, SSH, SMB, SQL, Web) that have zero legitimate business usage. Any interaction is a mathematically confirmed intrusion.

This Shuffle app enables security engineers and MSSP SOC teams to orchestrate end-to-end autonomous response workflows directly within Shuffle:
* **Instant Line-Rate Quarantine**: Automatically inject adversary IPs into DECTRAX's live External Dynamic List (EDL) feed consumed by Palo Alto, Fortinet, Check Point, pfSense, and Linux `nftables` firewalls.
* **Blocklist Auditing**: Programmatically inspect and verify active perimeter blocks across multi-tenant environments.
* **Deception Telemetry Triage**: Ingest high-fidelity breach forensics into Shuffle incident queues, tickets, and communication channels.
* **On-Demand Honeytoken Provisioning**: Automatically generate and distribute synthetic AWS keys, database credentials, JWTs, and Kerberos SPNs to detect insider threats and lateral movement.

---

## Authentication & Configuration

1. In the Shuffle Workflow Editor, add the **dectrax** app node.
2. Select or create an authentication credential:
   * **Parameter Name**: `apikey` (or configure via HTTP Header `Authorization: Bearer <API_KEY>`)
   * **Value**: Your DECTRAX API Bearer Token generated from the DECTRAX Management Console (`Settings -> API Keys`).
3. (Optional) Provide `base_url` if running a dedicated on-premise DECTRAX controller (default: `https://api.dectrax.com`).

---

## Actions Reference

### 1. `block_ip`
Publishes a confirmed attacker IP into DECTRAX's live External Dynamic List (EDL) feed for immediate sub-1.5s firewall drops.

* **Parameters:**
  * `apikey` (*string, required*): DECTRAX API Bearer Token.
  * `ip` (*string, required*): Malicious attacker IPv4 address to quarantine (e.g., `198.51.100.42`).
  * `reason` (*string, optional*): Justification note (default: `Shuffle SOAR Automated Interdiction`).
  * `base_url` (*string, optional*): Custom controller URL.

* **Sample Response:**
```json
{
  "status": "success",
  "message": "IP 198.51.100.42 added to active firewall EDL",
  "ip": "198.51.100.42",
  "interdiction_time_ms": 12
}
```

---

### 2. `get_blocked_ips`
Fetches the current active newline-delimited firewall blocklist consumed by perimeter edge devices.

* **Parameters:**
  * `apikey` (*string, required*): DECTRAX API Bearer Token.
  * `base_url` (*string, optional*): Custom controller URL.

* **Sample Response:**
```json
{
  "status": "success",
  "count": 2,
  "blocked_ips": [
    "198.51.100.42",
    "203.0.113.15"
  ]
}
```

---

### 3. `get_recent_threats`
Retrieves forensic threat records and honeypot interaction telemetry with 0.00% false positive accuracy.

* **Parameters:**
  * `apikey` (*string, required*): DECTRAX API Bearer Token.
  * `limit` (*integer, optional*): Maximum events to return (default: `50`).
  * `base_url` (*string, optional*): Custom controller URL.

* **Sample Response:**
```json
{
  "status": "success",
  "count": 1,
  "events": [
    {
      "timestamp": "2026-10-21T02:45:10Z",
      "source_ip": "198.51.100.42",
      "decoy_service": "RDP",
      "destination_port": 3389,
      "severity": "CRITICAL",
      "raw_payload": "Negotiate NTLMSSP Challenge/Response",
      "mitre_technique": "T1110.001"
    }
  ]
}
```

---

### 4. `generate_honeytoken`
Provisions synthetic canary tokens (AWS access keys, database credentials, JWTs, Kerberos SPNs) on demand.

* **Parameters:**
  * `apikey` (*string, required*): DECTRAX API Bearer Token.
  * `token_type` (*string, optional*): One of `aws_key`, `database_creds`, `jwt_token`, `kerberos_spn` (default: `aws_key`).
  * `memo` (*string, optional*): Location or host note (default: `Shuffle Automated Deployment`).
  * `base_url` (*string, optional*): Custom controller URL.

* **Sample Response:**
```json
{
  "status": "success",
  "token_id": "canary-9f82d1",
  "token_type": "aws_key",
  "credentials": {
    "access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  },
  "memo": "Finance-DB-AppServer-01"
}
```

---

## Example Shuffle Workflow

### Automated Decoy Breach Interdiction Playbook:
```
[Webhook / Schedule Trigger]
            │
            ▼
[DECTRAX: get_recent_threats] ─── (Iterate over new CRITICAL threat events)
            │
            ▼
[DECTRAX: block_ip] ──────────── (Line-rate drop on Palo Alto / Fortinet EDL in <1.5s)
            │
            ▼
[Slack / Microsoft Teams] ────── (Notify SOC: "Decoy RDP breach from 198.51.100.42 quarantined")
```

---

## Support & Enterprise Contact

* **Publisher**: DECTRAX Security Engineering
* **Website**: [https://dectrax.com](https://dectrax.com)
* **Technical Inquiries**: `support@dectrax.com`
* **License**: Apache License 2.0
