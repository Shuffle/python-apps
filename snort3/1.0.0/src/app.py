import asyncio
import json
import re
import subprocess

from walkoff_app_sdk.app_base import AppBase


class snort3(AppBase):
    __version__ = "1.0.0"
    app_name = "snort3"

    def __init__(self, redis, logger, console_logger=None):
        super().__init__(redis, logger, console_logger)

    def create_snort_file(self, file_ref):

        print(f"Retrieving file {file_ref}.")

        re_hash = re.compile("[a-fA-F0-9]{8}-([a-fA-F0-9]{4}-){3}[a-fA-F0-9]{12}")
        if re_hash.match(file_ref) is None:
            raise (ValueError("File reference must be a supported hash value."))

        target_dir = "/app"
        ref_dict = self.get_file(file_ref)

        target_path = target_dir + "/" + ref_dict["filename"]
        with open(target_path, "xb") as tmp_file:
            tmp_file.write(ref_dict["data"])
            tmp_file.close()

        return target_path

    def run_snort_scan(self, config_path, rules_path, pcap_path):

        cmd = [
            "snort",
            "-c",
            config_path,
            "-R",
            rules_path,
            "-r",
            pcap_path,
            "-A",
            "alert_fast",
        ]
        print("Executing the following command: {}".format(" ".join(cmd)))
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        alerts = []
        for line in result.stdout.split("\n"):
            if "[**]" in line:
                alerts.append(line)

        return_data = {
            "success": True,
            "return_code": result.returncode,
            "alerts": alerts,
            "errors": result.stderr,
            "pcap": {"name": pcap_path},
            "cmd": cmd,
        }
        return return_data

    def simple_analyze_file(self, config_file, rules_file, pcap_file):

        rules_path = self.create_snort_file(rules_file)
        pcap_path = self.create_snort_file(pcap_file)

        config_path = "/usr/local/etc/snort/snort.lua"
        if len(config_file) > 0:
            config_path = self.create_snort_file(config_file)

        return_data = self.run_snort_scan(config_path, rules_path, pcap_path)

        try:
            return json.dumps(return_data)
        except (json.JSONDecodeError, TypeError):
            return return_data

    def version_check(self):

        result = subprocess.run(
            ["snort", "-V", "-u", "snort3"], capture_output=True, text=True
        )

        return_data = {
            "success": True,
            "return_code": result.returncode,
            "output": result.stdout,
            "errors": result.stderr,
        }

        try:
            return json.dumps(return_data)
        except (json.JSONDecodeError, TypeError):
            return return_data

    def custom_rule_scan(self, config_file, custom_rule, pcap_file):

        pcap_path = self.create_snort_file(pcap_file)

        config_path = "/usr/local/etc/snort/snort.lua"
        if len(config_file) > 0:
            config_path = self.create_snort_file(config_file)

        rules_path = "/app/my.rules"
        with open(rules_path, "xb") as tmp_file:
            tmp_file.write(custom_rule.encode("utf-8"))
            tmp_file.close()

        return_data = self.run_snort_scan(config_path, rules_path, pcap_path)

        try:
            return json.dumps(return_data)
        except (json.JSONDecodeError, TypeError):
            return return_data


if __name__ == "__main__":
    snort3.run()
