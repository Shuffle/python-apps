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

    async def auth_ec2(self, access_key, secret_key, region):
        my_config = Config(
            region_name = region,
            signature_version = 'v4',
            retries = {
                'max_attempts': 10,
                'mode': 'standard'
            },
        )

        self.ec2 = boto3.resource(
            'ec2', 
            config=my_config, 
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        return self.ec2

    # Write your data inside this function
    async def get_rules(self, access_key, secret_key, region, ACL_id):
        self.ec2 = await self.auth_ec2(access_key, secret_key, region)

        network_acl = self.ec2.NetworkAcl(ACL_id)
        return network_acl.entries

    # Write your data inside this function
    async def block_ip(self, access_key, secret_key, region, ACL_id, ip, direction):
        self.ec2 = await self.auth_ec2(access_key, secret_key, region)
        network_acl = self.ec2.NetworkAcl(ACL_id)

        if "/" not in ip:
            ip = "%s/32" % ip

        egress = True 
        if direction == "inbound":
            egress = False

        # This is a shitty system :)
        minimum = 100
        max_range = 30000
        numbers = []
        found = False
        for item in network_acl.entries:
            if egress != item["Egress"]:
                continue

            if ip == item["CidrBlock"]:
                raise Exception("IP %s is already being blocked." % ip)

            numbers.append(item["RuleNumber"])


        for index in range(minimum, max_range):
            if index in numbers:
                continue

            minimum = index
            break

        print("New number: %d" % minimum)

        try:
            return network_acl.create_entry(
                CidrBlock=ip,
                DryRun=False,
                Egress=egress,
                IcmpTypeCode={
                    'Code': 123,
                    'Type': 123
                },
                PortRange={
                    'From': 0,
                    'To': 65535
                },
                Protocol="6",
                RuleAction="DENY",
                RuleNumber=minimum,
            )
        except botocore.exceptions.ClientError as e:
            print("Error: %s" % e)
            return e


    # Write your data inside this function
    async def create_acl_entry(self, access_key, secret_key, region, ACL_id, cidr_block, dryrun, direction, portrange_from, portrange_to, protocol, rule_action, rule_number):
        self.ec2 = await self.auth_ec2(access_key, secret_key, region)

        network_acl = self.ec2.NetworkAcl(ACL_id)
        if protocol.lower() == "tcp":
            protocol = "6"
        elif protocol.lower() == "udp":
            protocol = "17"

        egress = True 
        if direction == "inbound":
            egress = False
        else:
            egress = True

        if dryrun.lower() == "false":
            dryrun = False
        else:
            dryrun = True

        try:
            return network_acl.create_entry(
                CidrBlock=cidr_block,
                DryRun=dryrun,
                Egress=egress,
                IcmpTypeCode={
                    'Code': 123,
                    'Type': 123
                },
                PortRange={
                    'From': int(portrange_from),
                    'To': int(portrange_to)
                },
                Protocol=protocol,
                RuleAction=rule_action,
                RuleNumber=int(rule_number),
            )
        except botocore.exceptions.ClientError as e:
            print("Error: %s" % e)
            return e


if __name__ == "__main__":
    asyncio.run(AWSEC2.run(), debug=True)
