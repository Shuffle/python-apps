import socket
import asyncio
import time
import random
import json
import requests

import io
import boto3
from botocore.exceptions import ClientError

import urllib3

from walkoff_app_sdk.app_base import AppBase


class DktLambda(AppBase):
    __version__ = "1.0.0"
    app_name = "dkt-lambda"

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        super().__init__(redis, logger, console_logger)


    def auth_lambda(self, access_key, secret_key, region):

        return boto3.client(
            'lambda',
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )


    def invoke_function(self, access_key, secret_key, region, function_name, function_params, get_log=False):
        """
        Invokes a Lambda function.

        :param function_name: The name of the function to invoke.
        :param function_params: The parameters of the function as a dict. This dict
                                is serialized to JSON before it is sent to Lambda.
        :param get_log: When true, the last 4 KB of the execution log are included in
                        the response.
        :return: The response from the function invocation.
        """
        client = self.auth_lambda(access_key, secret_key, region)

        try:
            response = client.invoke(FunctionName=function_name, Payload=json.dumps(function_params), LogType='Tail' if get_log else 'None')
            response_data = json.loads(response['Payload'].read())
            if 'errorMessage' in response_data:
                ret_response = {"success": False, "reason": "Function timed out"}
            else:
                ret_response = {"success": True, "results": response_data[0]}
        except ClientError:
            raise
            response_error = json.loads('{"success": False, "reason": "Couldn\'t invoke function ' + function_name + '"}')
            return response_error

        return ret_response


if __name__ == "__main__":
    DktLambda.run()
