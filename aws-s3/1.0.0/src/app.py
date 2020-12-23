import socket
import asyncio
import time
import random
import json
import boto3
import botocore
from botocore.config import Config

from walkoff_app_sdk.app_base import AppBase

class AWSEC2(AppBase):
    __version__ = "1.0.0"
    app_name = "AWS ec2"  

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    async def auth_s3(self, access_key, secret_key, region):
        my_config = Config(
            region_name = region,
            signature_version = "s3v4",
            retries = {
                'max_attempts': 10,
                'mode': 'standard'
            },
        )

        self.s3 = boto3.resource(
            's3', 
            config=my_config, 
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        return self.s3

    async def list_buckets(self, access_key, secret_key, region):
        self.s3 = await self.auth_s3(access_key, secret_key, region)
        client = self.s3.meta.client
        try:
            newlist = client.list_buckets()
            return newlist
        except botocore.exceptions.ClientError as e:
            return "Error: %s" % e

    async def create_bucket(self, access_key, secret_key, region, bucket_name, access_type):
        self.s3 = await self.auth_s3(access_key, secret_key, region)
        client = self.s3.meta.client
        try:
            creation = client.create_bucket(
                Bucket=bucket_name,
                ACL=access_type,
                CreateBucketConfiguration={
                    'LocationConstraint': region
                },
            )

            return creation 
        except botocore.exceptions.ClientError as e:
            return "Error: %s" % e


if __name__ == "__main__":
    asyncio.run(AWSEC2.run(), debug=True)
