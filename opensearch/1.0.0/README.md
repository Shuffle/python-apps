# OpenSearch

OpenSearch Shuffle app using mutual TLS (client certificate) authentication.

## Authentication

Configure the following in the app authentication section:

- `base_url`: OpenSearch base URL (e.g. `https://opensearch.example.com:9200`).
- `client_cert`: Client certificate (PEM) file ID.
- `client_key`: Client private key (PEM) file ID.
- `ca_cert` (optional): CA certificate (PEM) file ID used for TLS verification.
- `verify` (optional): `true` or `false`.
- `timeout` (optional): Request timeout in seconds.

Notes:
- If your client certificate file already contains the private key, upload the same file for both `client_cert` and `client_key`.
- If `verify` is `true` and `ca_cert` is provided, the CA cert is used for TLS verification.

## Actions

- `cluster_health`: Get cluster health status.
- `list_indices`: List indices via `_cat/indices`.
- `get_index`: Get index settings and mappings.
- `create_index`: Create an index with settings/mappings.
- `delete_index`: Delete an index.
- `index_document`: Index a document by ID.
- `create_document`: Create a document with an auto-generated ID.
- `get_document`: Get a document by ID.
- `update_document`: Update a document by ID.
- `delete_document`: Delete a document by ID.
- `search`: Search an index by query DSL or query string.
- `bulk`: Bulk index/update/delete (NDJSON).
- `raw_request`: Send a custom request to any OpenSearch endpoint.

## Local development

From this version directory:

```bash
docker build -t shuffle-opensearch:1.0.0 .
docker run --rm shuffle-opensearch:1.0.0
```

Or run locally:

```bash
pip install -r requirements.txt
python src/app.py --log-level DEBUG
```
