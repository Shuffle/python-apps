import asyncio
import json
import subprocess

from walkoff_app_sdk.app_base import AppBase


class snort3(AppBase):
    __version__ = "1.0.0"
    app_name = "snort3"

    def __init__(self, redis, logger, console_logger=None):
        super().__init__(redis, logger, console_logger)

    async def create_snort_file(self, file_ref):

        target_dir = "/app"
        print(f"Retrieving file {file_ref}.")
        ref_dict = self.get_file(file_ref)

        target_path = target_dir + "/" + ref_dict["filename"]
        with open(target_path, "xb") as tmp_file:
            tmp_file.write(ref_dict["data"])
            tmp_file.close()

        return target_path

    async def simple_analyze_file(self, config_file, rules_file, pcap_file):

        rules_path = await self.create_snort_file(rules_file)
        pcap_path = await self.create_snort_file(pcap_file)

        config_path = "/usr/local/etc/snort/snort.lua"
        if len(config_file) > 0:
            config_path = await self.create_snort_file(config_file)

        cmd = " ".join(
            [
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
        )
        print("Executing the following command: {}".format(cmd))
        result = subprocess.run(
            [
                "snort",
                "-c",
                config_path,
                "-R",
                rules_path,
                "-r",
                pcap_path,
                "-A",
                "alert_fast",
                "-u",
                "snort3",
            ],
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
            "pcap": {"ref": pcap_file, "name": pcap_path},
            "cmd": cmd,
        }

        try:
            return json.dumps(return_data)
        except (json.JSONDecodeError, TypeError):
            return return_data

    async def version_check(self):

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


if __name__ == "__main__":
    asyncio.run(snort3.run(), debug=True)
