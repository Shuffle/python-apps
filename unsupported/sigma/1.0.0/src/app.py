import socket
import asyncio
import time
import random
import json

from walkoff_app_sdk.app_base import AppBase

# 1. Generate the api.yaml based on downloaded files
# 2. Add a way to choose the rule and the target platform for it
# 3. Add the possibility of translating rules back and forth

# 4. Make it so you can start with Mitre Att&ck techniques 
# and automatically get the right rules set up with your tools :O
class Sigma(AppBase):
    __version__ = "1.0.0"
    app_name = "python_playground"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    def run_me_1(self, json_data): 
        return "Ran function 1"

    def run_me_2(self, json_data): 
        return "Ran function 2"

    def run_me_3(self, json_data): 
        return "Ran function 3"

    # Write your data inside this function
    async def run_python_script(self, json_data, function_to_execute):
        # It comes in as a string, so needs to be set to JSON
        try:
            json_data = json.loads(json_data)
        except json.decoder.JSONDecodeError as e:
            return "Couldn't decode json: %s" % e

        # These are functions
        switcher = {
            "function_1" : self.run_me_1,
            "function_2" : self.run_me_2,
            "function_3" : self.run_me_3,
        }

        func = switcher.get(function_to_execute, lambda: "Invalid function")
        return func(json_data)

if __name__ == "__main__":
    asyncio.run(Sigma.run(), debug=True)
