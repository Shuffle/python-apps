# Sigma Translator App v1.1.0

A modern Sigma rule translator for Shuffle that converts Sigma detection rules to various SIEM query languages using the pySigma framework.

## Features

- **Modern pySigma Integration**: Uses the latest pySigma library instead of legacy sigmatools
- **Multiple SIEM Support**: Supports 12+ SIEM platforms including Splunk, Elasticsearch, Microsoft Sentinel, QRadar, and more
- **Rule Validation**: Validates Sigma rules for syntax and structure
- **Multiple Output Formats**: Supports default, JSON, and YAML output formats
- **File Integration**: Works with Shuffle's file storage system

## Supported Platforms

- **Splunk**: SPL queries
- **Elasticsearch**: Lucene queries  
- **Microsoft Sentinel**: KQL queries
- **IBM QRadar**: AQL queries
- **LogPoint**: LogPoint queries
- **CrowdStrike**: CrowdStrike queries
- **Carbon Black**: Carbon Black queries
- **Rapid7 InsightIDR**: LEQL queries
- **Panther**: Panther queries
- **OpenSearch**: Lucene queries
- **Grafana Loki**: LogQL queries
- **SQLite**: SQL queries

## Actions

### translate_sigma_rule
Translates a Sigma rule to a specific SIEM query language.

**Parameters:**
- `sigma_rule` (required): The Sigma rule in YAML format
- `target_platform` (required): Target SIEM platform (e.g., "splunk", "elasticsearch")
- `output_format` (optional): Output format ("default", "json", "yaml")

### validate_sigma_rule
Validates a Sigma rule for syntax and structure.

**Parameters:**
- `sigma_rule` (required): The Sigma rule in YAML format to validate

### list_supported_platforms
Lists all supported SIEM platforms and their capabilities.

**Parameters:** None

### convert_rule_file
Converts a Sigma rule file from Shuffle file storage.

**Parameters:**
- `file_id` (required): The Shuffle file ID containing the Sigma rule
- `target_platform` (required): Target SIEM platform

## Example Usage

### Basic Translation
```yaml
title: Suspicious Process Creation
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    Image|endswith: '\cmd.exe'
    CommandLine|contains: 'whoami'
  condition: selection
```

This rule can be translated to Splunk SPL, Elasticsearch Lucene, Microsoft Sentinel KQL, and other supported formats.

## Dependencies

- pySigma v0.11.23+
- Multiple pySigma backend packages
- PyYAML for YAML processing
- JSONSchema for validation

## Version History

- **v1.1.0**: Complete rewrite using modern pySigma framework
- **v1.0.0**: Legacy implementation using sigmatools (deprecated)

## Related Links

- [Sigma Detection Format](https://sigmahq.io/)
- [pySigma Documentation](https://sigmahq-pysigma.readthedocs.io/)
- [Shuffle Documentation](https://shuffler.io/docs)
