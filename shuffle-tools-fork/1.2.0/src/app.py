import hmac
import datetime
import json
import time
import markupsafe
import os
import re
import subprocess
import tempfile
import zipfile
import base64
import ipaddress
import hashlib
import shufflepy
from io import StringIO
from contextlib import redirect_stdout
import random
import string

import xmltodict
from json2xml import json2xml
from json2xml.utils import readfromstring

from ioc_finder import find_iocs
from dateutil.parser import parse as dateutil_parser
from google.auth import crypt
from google.auth import jwt

import py7zr
import pyminizip
import rarfile
import requests
import tarfile
import binascii
import struct

import paramiko
import concurrent.futures
import multiprocessing

from walkoff_app_sdk.app_base import AppBase

class Tools(AppBase):
    __version__ = "1.2.0"
    app_name = (
        "Shuffle Tools Fork"  # this needs to match "name" in api.yaml for WALKOFF to work
    )

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    def execute_python(self, code):
        if len(code) == 36 and "-" in code:
            filedata = self.get_file(code)
            if filedata["success"] == False:
                return {
                    "success": False,
                    "message": f"Failed to get file for ID {code}",
                }

            if ".py" not in filedata["filename"]:
                return {
                    "success": False,
                    "message": f"Filename needs to contain .py",
                }


        # Write the code to a file
        # 1. Take the data into a file
        # 2. Subprocess execute file?
        try:
            f = StringIO()
            def custom_print(*args, **kwargs):
                return print(*args, file=f, **kwargs)
            
            #with redirect_stdout(f): # just in case
            # Add globals in it too
            globals_copy = globals().copy()
            globals_copy["print"] = custom_print

            # Add self to globals_copy
            for key, value in locals().copy().items():
                if key not in globals_copy:
                    globals_copy[key] = value

            globals_copy["self"] = self

            exec(code, globals_copy)

            s = f.getvalue()
            f.close() # why: https://www.youtube.com/watch?v=6SA6S9Ca5-U

            #try:
            #    s = s.encode("utf-8")
            #except Exception as e:

            try:
                return {
                    "success": True,
                    "message": json.loads(s.strip()),
                }
            except Exception as e:
                try:
                    return {
                        "success": True,
                        "message": s.strip(),
                    }
                except Exception as e:
                    return {
                        "success": True,
                        "message": s,
                    }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"exception: {e}",
            }

if __name__ == "__main__":
    Tools.run()
