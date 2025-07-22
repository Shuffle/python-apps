import os
import json
import yaml
import tempfile
import traceback
from typing import Dict, List, Optional, Any

from shuffle_sdk import AppBase

# pySigma imports
from sigma.rule import SigmaRule
from sigma.collection import SigmaCollection
from sigma.exceptions import SigmaError, SigmaParseError

# Backend imports
try:
    from sigma.backends.splunk import SplunkBackend
    from sigma.pipelines.splunk import splunk_windows_pipeline
except ImportError:
    SplunkBackend = None

try:
    from sigma.backends.elasticsearch import LuceneBackend
    from sigma.pipelines.elasticsearch import ecs_windows_pipeline
except ImportError:
    LuceneBackend = None

try:
    from sigma.backends.kusto import KustoBackend
    from sigma.pipelines.microsoft365defender import microsoft_365_defender_pipeline
except ImportError:
    KustoBackend = None

try:
    from sigma.backends.qradar import QRadarBackend
except ImportError:
    QRadarBackend = None

try:
    from sigma.backends.logpoint import LogPointBackend
except ImportError:
    LogPointBackend = None

try:
    from sigma.backends.crowdstrike import CrowdStrikeBackend
except ImportError:
    CrowdStrikeBackend = None

try:
    from sigma.backends.carbonblack import CarbonBlackBackend
except ImportError:
    CarbonBlackBackend = None

try:
    from sigma.backends.insightidr import InsightIDRBackend
except ImportError:
    InsightIDRBackend = None

try:
    from sigma.backends.panther import PantherBackend
except ImportError:
    PantherBackend = None

try:
    from sigma.backends.opensearch import OpensearchLuceneBackend
except ImportError:
    OpensearchLuceneBackend = None

try:
    from sigma.backends.loki import LokiBackend
except ImportError:
    LokiBackend = None

try:
    from sigma.backends.sqlite import SqliteBackend
except ImportError:
    SqliteBackend = None


class Sigma(AppBase):
    __version__ = "1.1.0"
    app_name = "sigma"

    def __init__(self, redis, logger, console_logger=None):
        """
        Initialize the Sigma app with Redis and logging.
        """
        super().__init__(redis, logger, console_logger)
        
        # Define supported backends
        self.backends = {
            "splunk": {
                "backend": SplunkBackend,
                "pipeline": splunk_windows_pipeline if 'splunk_windows_pipeline' in globals() else None,
                "description": "Splunk SPL queries"
            },
            "elasticsearch": {
                "backend": LuceneBackend,
                "pipeline": ecs_windows_pipeline if 'ecs_windows_pipeline' in globals() else None,
                "description": "Elasticsearch Lucene queries"
            },
            "microsoft-sentinel": {
                "backend": KustoBackend,
                "pipeline": microsoft_365_defender_pipeline if 'microsoft_365_defender_pipeline' in globals() else None,
                "description": "Microsoft Sentinel KQL queries"
            },
            "qradar": {
                "backend": QRadarBackend,
                "pipeline": None,
                "description": "IBM QRadar AQL queries"
            },
            "logpoint": {
                "backend": LogPointBackend,
                "pipeline": None,
                "description": "LogPoint queries"
            },
            "crowdstrike": {
                "backend": CrowdStrikeBackend,
                "pipeline": None,
                "description": "CrowdStrike queries"
            },
            "carbonblack": {
                "backend": CarbonBlackBackend,
                "pipeline": None,
                "description": "Carbon Black queries"
            },
            "insightidr": {
                "backend": InsightIDRBackend,
                "pipeline": None,
                "description": "Rapid7 InsightIDR LEQL queries"
            },
            "panther": {
                "backend": PantherBackend,
                "pipeline": None,
                "description": "Panther queries"
            },
            "opensearch": {
                "backend": OpensearchLuceneBackend,
                "pipeline": None,
                "description": "OpenSearch Lucene queries"
            },
            "loki": {
                "backend": LokiBackend,
                "pipeline": None,
                "description": "Grafana Loki LogQL queries"
            },
            "sqlite": {
                "backend": SqliteBackend,
                "pipeline": None,
                "description": "SQLite queries"
            }
        }

    def _parse_sigma_rule(self, sigma_rule: str) -> SigmaRule:
        """
        Parse a Sigma rule from YAML string.
        """
        try:
            # Parse YAML
            rule_dict = yaml.safe_load(sigma_rule)
            
            # Create SigmaRule object
            sigma_rule_obj = SigmaRule.from_dict(rule_dict)
            return sigma_rule_obj
            
        except yaml.YAMLError as e:
            raise SigmaParseError(f"Invalid YAML format: {str(e)}")
        except Exception as e:
            raise SigmaError(f"Failed to parse Sigma rule: {str(e)}")

    def _get_backend(self, platform: str):
        """
        Get the appropriate backend for the target platform.
        """
        if platform not in self.backends:
            available_platforms = list(self.backends.keys())
            raise ValueError(f"Unsupported platform '{platform}'. Available platforms: {available_platforms}")
        
        backend_info = self.backends[platform]
        backend_class = backend_info["backend"]
        
        if backend_class is None:
            raise ImportError(f"Backend for '{platform}' is not available. Please install the required package.")
        
        # Initialize backend
        backend = backend_class()
        
        # Apply pipeline if available
        pipeline = backend_info["pipeline"]
        if pipeline:
            backend.pipeline = pipeline
            
        return backend

    def translate_sigma_rule(self, sigma_rule: str, target_platform: str, output_format: str = "default") -> str:
        """
        Translate a Sigma rule to a specific SIEM query language.
        """
        try:
            self.logger.info(f"Translating Sigma rule to {target_platform}")
            
            # Parse the Sigma rule
            rule = self._parse_sigma_rule(sigma_rule)
            
            # Get the appropriate backend
            backend = self._get_backend(target_platform)
            
            # Convert the rule
            queries = backend.convert(rule)
            
            # Format output
            if output_format == "json":
                result = {
                    "platform": target_platform,
                    "queries": queries,
                    "rule_title": rule.title if hasattr(rule, 'title') else "Unknown",
                    "rule_id": str(rule.id) if hasattr(rule, 'id') else None
                }
                return json.dumps(result, indent=2)
            elif output_format == "yaml":
                result = {
                    "platform": target_platform,
                    "queries": queries,
                    "rule_title": rule.title if hasattr(rule, 'title') else "Unknown",
                    "rule_id": str(rule.id) if hasattr(rule, 'id') else None
                }
                return yaml.dump(result, default_flow_style=False)
            else:
                # Default format - return queries as string
                if isinstance(queries, list):
                    return "\n".join(queries)
                else:
                    return str(queries)
                    
        except Exception as e:
            error_msg = f"Translation failed: {str(e)}\n{traceback.format_exc()}"
            self.logger.error(error_msg)
            return f"Error: {str(e)}"

    def validate_sigma_rule(self, sigma_rule: str) -> str:
        """
        Validate a Sigma rule for syntax and structure.
        """
        try:
            self.logger.info("Validating Sigma rule")
            
            # Parse the rule
            rule = self._parse_sigma_rule(sigma_rule)
            
            # Basic validation checks
            validation_results = {
                "valid": True,
                "title": getattr(rule, 'title', None),
                "id": str(getattr(rule, 'id', None)) if getattr(rule, 'id', None) else None,
                "status": getattr(rule, 'status', None),
                "level": getattr(rule, 'level', None),
                "logsource": getattr(rule, 'logsource', None),
                "detection": bool(getattr(rule, 'detection', None)),
                "warnings": []
            }
            
            # Check for required fields
            if not validation_results["title"]:
                validation_results["warnings"].append("Missing title field")
            
            if not validation_results["detection"]:
                validation_results["warnings"].append("Missing or invalid detection section")
            
            if not validation_results["logsource"]:
                validation_results["warnings"].append("Missing logsource section")
            
            return json.dumps(validation_results, indent=2)
            
        except Exception as e:
            error_result = {
                "valid": False,
                "error": str(e),
                "details": traceback.format_exc()
            }
            return json.dumps(error_result, indent=2)

    def list_supported_platforms(self) -> str:
        """
        List all supported SIEM platforms and their capabilities.
        """
        try:
            platforms = {}
            
            for platform, info in self.backends.items():
                platforms[platform] = {
                    "description": info["description"],
                    "available": info["backend"] is not None,
                    "has_pipeline": info["pipeline"] is not None
                }
            
            result = {
                "supported_platforms": platforms,
                "total_count": len(platforms),
                "available_count": sum(1 for p in platforms.values() if p["available"])
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error listing platforms: {str(e)}"

    def convert_rule_file(self, file_id: str, target_platform: str) -> str:
        """
        Convert a Sigma rule file from Shuffle file storage.
        """
        try:
            self.logger.info(f"Converting rule file {file_id} to {target_platform}")
            
            # Get file content from Shuffle
            file_content = self.get_file(file_id)
            
            if not file_content:
                return "Error: Could not retrieve file content"
            
            # Convert bytes to string if necessary
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8')
            
            # Translate the rule
            return self.translate_sigma_rule(file_content, target_platform)
            
        except Exception as e:
            error_msg = f"File conversion failed: {str(e)}"
            self.logger.error(error_msg)
            return f"Error: {str(e)}"


if __name__ == "__main__":
    Sigma.run()
