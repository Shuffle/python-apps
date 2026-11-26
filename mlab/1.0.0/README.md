## mlab.sh App
[mlab.sh](https://mlab.sh) app for Shuffle: domain, IP, crypto, file, hash, URL, email, phone and MAC scanning, IOC extraction, CVE intelligence and threat-actor data.

## Actions

| No. | Action | Description | Parameters |
|-----|--------|-------------|------------|
|1 | scan_domain | Launch a domain scan. With `wait_for_completion=true` (default) it polls until done and returns the full results (subdomains, DNS, SSL, security.txt). | **domain**, wait_for_completion, timeout
|2 | get_domain_status | Status of a domain scan | **domain**
|3 | get_domain_results | Results of a finished domain scan | **domain**
|4 | get_domain_ssl | SSL certificates seen for a domain | **domain**
|5 | capture_network_requests | Load a page and capture every network request it makes | **page_url**
|6 | lookup_ip | Geolocation, ASN and ownership for an IPv4/IPv6 address | **ip**
|7 | lookup_crypto | Sanctions, labels and risk score for a crypto address (chain blank = auto-detect) | **address**, chain
|8 | bulk_lookup_crypto | Look up many addresses, sent in batches of 100 | ***addresses***, chain
|9 | lookup_hash | Known-good / known-malicious verdict for an MD5, SHA-1, SHA-256 or SHA-512 | **hash**
|10 | bulk_lookup_hash | Look up many hashes, sent in batches of 500 | ***hashes***
|11 | upload_file | Upload a Shuffle file (max 10 MB) for analysis, returns its sha256 | **file_id**
|12 | get_file_results | Analysis results for an uploaded file | **sha256**
|13 | get_file_tool_output | Raw output of one tool listed in the file results | **sha256**, **tool**
|14 | analyze_url | Phishing shapes, embedded redirects and what mlab knows about the host | **target_url**, resolve
|15 | analyze_email | Mailbox type, spoofability of the domain and risk score | **email**
|16 | analyze_phone | Validity, line type, operator and scam shapes (E.164) | **number**
|17 | lookup_mac | Vendor, randomization, virtualization and every notation | **mac**
|18 | extract_iocs | Pull every indicator out of raw text, with optional SMS threat scoring (`fast` / `deep`) | **text**, risk, country
|19 | get_quota | Remaining daily quota for a scan type (domain / ip / file / crypto) | **scan_type**
|20 | search_cves | Search CVEs by keyword, vendor or product | **query**, severity, published_after, exact, kev_only
|21 | get_cve | Full CVE detail including EPSS and KEV | **cve_id**
|22 | get_latest_cves | Vulnerabilities from the last 7 days | 
|23 | list_threat_actors | List / search threat actors | origin, motivation, sector, limit, offset
|24 | get_threat_actor | A threat actor by slug, with aliases, tools, CVEs and techniques | **slug**
|25 | get_actors_by_cve | Threat actors known to exploit a CVE | **cve_id**

__Note__:
- apikey and url are used for authentication (url defaults to `https://mlab.sh/api/v1`, only change it for self-hosted instances).
- CVE and threat-actor actions call the public `vuln.mlab.sh` and `actors.mlab.sh` APIs and ignore the key.
- **Bold** parameters are required.
- ***Bold italic*** parameters take a list separated by commas, spaces or new lines.
- Actions return the raw mlab.sh JSON. On an HTTP error they return `{"success": false, "status": <code>, "error": <body>}`.

## Requirements

1. An mlab.sh account.
2. An API key: **mlab.sh → Account → Settings → API Keys** (starts with `mlab_`).

## Example workflows

- **IP enrichment:** `lookup_ip` → `get_quota` (scan_type `ip`).
- **Domain recon:** `scan_domain` (wait_for_completion `true`) → `get_domain_ssl` → `get_quota` (scan_type `domain`).
- **Threat context for a CVE:** `get_cve` → `get_actors_by_cve` with `$get_cve.id`.
- **Phishing triage:** `extract_iocs` on an email body → `analyze_url` / `bulk_lookup_hash` on what it found.
