import os
import socket
import asyncio
import time
import random
import json
import subprocess
import requests
import tempfile
import gnupg
import zipfile
import shutil


from walkoff_app_sdk.app_base import AppBase


class Gpg(AppBase):
    """
    An example of a Walkoff App.
    Inherit from the AppBase class to have Redis, logging, and console logging set up behind the scenes.
    """

    __version__ = "1.1.0"
    app_name = "Gpg Tools"

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)
        
    def extract_archive(self, zip_file_id, fileformat="zip", password=None):
        try:
            return_data = {"success": False, "files": []}
            to_be_uploaded = []
            item = self.get_file(zip_file_id)
            return_ids = None

            self.logger.info("Working with fileformat %s" % fileformat)
            with tempfile.TemporaryDirectory() as tmpdirname:

                # Get archive and save phisically
                with open(os.path.join(tmpdirname, "archive"), "wb") as f:
                    f.write(item["data"])

                # Grab files before, upload them later

                # Zipfile for zipped archive
                if fileformat.strip().lower() == "zip":
                    try:
                        self.logger.info("Starting zip extraction")
                        with zipfile.ZipFile(os.path.join(tmpdirname, "archive")) as z_file:
                            if password:
                                self.logger.info("In zip extraction with password")
                                z_file.setpassword(bytes(password.encode()))

                            self.logger.info("Past zip extraction")
                            for member in z_file.namelist():
                                filename = os.path.basename(member)
                                if not filename:
                                    continue

                                source = z_file.open(member)
                                to_be_uploaded.append(
                                    {"filename": source.name.split("/")[-1], "data": source.read()}
                                )

                                return_data["success"] = True
                    except (zipfile.BadZipFile, Exception):
                        return_data["files"].append(
                            {
                                "success": False,
                                "file_id": zip_file_id,
                                "filename": item["filename"],
                                "message": "File is not a valid zip archive",
                            }
                        )
                else:
                    return "No such format: %s" % fileformat

            self.logger.info("Breaking as this only handles one archive at a time.")
            if len(to_be_uploaded) > 0:
                return_ids = self.set_files(to_be_uploaded)
                self.logger.info(f"Got return ids from files: {return_ids}")

                for i in range(len(return_ids)):
                    return_data["archive_id"] = zip_file_id
                    try:
                        return_data["files"].append(
                            {
                                "success": True,
                                "file_id": return_ids[i],
                                "filename": to_be_uploaded[i]["filename"],
                            }
                        )
                    except:
                        return_data["files"].append(
                            {
                                "success": True,
                                "file_id": return_ids[i],
                            }
                        )
            else:
                self.logger.info(f"No file ids to upload.")
                return_data["success"] = False
                return_data["files"].append(
                    {
                        "success": False,
                        "filename": "No data in archive",
                        "message": "Archive is empty",
                    }
                )

            return return_data
        
        except Exception as excp:
            return {"success": False, "message": "%s" % excp}
   
    def get_auth(self, file_id):
        item = self.get_file(file_id)
        tmpdirname = f"/tmp/{file_id}"

        # Clean up all old stuff
        if os.path.exists(tmpdirname):
            shutil.rmtree(tmpdirname, )

        # Get archive and save physically
        os.mkdir(tmpdirname)
        with open(os.path.join(tmpdirname, "archive"), "wb") as f:
            f.write(item["data"])

        # Grab files before, upload them later
        gpgfound = False
        with zipfile.ZipFile(os.path.join(tmpdirname, "archive")) as z_file:
            print("Past zip extraction")
            for member in z_file.namelist():
                print(member)
                if member == ".gnupg/":
                    gpgfound = True 

                z_file.extract(member, tmpdirname)

        os.remove(os.path.join(tmpdirname, "archive"))

        if gpgfound: 
            tmpdirname = os.path.join(tmpdirname, ".gnupg")

        try:
            gpg = gnupg.GPG(gnupghome=tmpdirname)
        except TypeError:
            gpg = gnupg.GPG(homedir=tmpdirname)

        return gpg
    
    def cleanup(self, zip_file_id):
        
        tmpdirname = f"/tmp/{zip_file_id}"
        
        if os.path.exists(tmpdirname):
            shutil.rmtree(tmpdirname)
        self.logger.debug(">> Cleanup complete")

        return

        
    def decrypt_text(
        self, zip_file_id, encrypted_text, password, always_trust
    ):
        gpg = self.get_auth(zip_file_id)
        self.logger.debug(">> Created GPG instance")
        
        decrypted_text = gpg.decrypt(
                encrypted_text,
                passphrase=password,
                always_trust=always_trust
        )
        
        # Delete the downloaded keystore
        self.cleanup(zip_file_id)
        
        if decrypted_text.ok:      
            return {"success": True, "data": decrypted_text.data.decode('utf-8')}
        else:
            return {"success": False, "error": decrypted_text.stderr }
        
        
        
    def encrypt_text(
        self, zip_file_id, clear_text, recipients, always_trust
    ):
        gpg = self.get_auth(zip_file_id)
        self.logger.debug(">> Created GPG instance")
        
        # Build list of recipients from comma-separated string
        recipients = recipients.split(',')
        
        self.logger.debug(f">> Recipients: {recipients}")
        
        encrypted_text = gpg.encrypt(
                clear_text,
                recipients=recipients,
                always_trust=always_trust
        )
        
        # Delete the downloaded keystore
        self.cleanup(zip_file_id)
        
        if encrypted_text.ok:      
            return {"success": True, "data": encrypted_text.data.decode('utf-8')}
        else:
            return {"success": False, "error": encrypted_text.stderr }


    def decrypt_file(
        self, zip_file_id, password, file_id, output_name, always_trust
    ):
        gpg = self.get_auth(zip_file_id)
        self.logger.debug(">> Created GPG instance")
        
        if file_id["success"] == False:
            return "Error managing files."
        
        always_trust = True if always_trust.lower() == "true" else False

        ret_decrypt = gpg.decrypt(
                file_id["data"],
                passphrase=password,
                always_trust=always_trust,
            )
        
        # Delete the downloaded keystore
        self.cleanup(zip_file_id)
        
        if ret_decrypt.ok:
            self.logger.debug(">> File decrypted")

            file_id = self.set_files([{"filename": output_name, "data": ret_decrypt.data}])
            if len(file_id) == 1:
                file_id = file_id[0]
            return {"success": True, "id": file_id}
        else:
            return {"success": False, "error": ret_decrypt.stderr}

    def encrypt_file(
        self, zip_file_id, file_id, output_name, recipients, always_trust
    ):
        gpg = self.get_auth(zip_file_id)
        self.logger.debug(">> Created GPG instance")
        
        if file_id["success"] == False:
            return "Error managing files."
        
        always_trust = True if always_trust.lower() == "true" else False

        # Build list of recipients from comma-separated string
        recipients = recipients.split(',')
        
        self.logger.debug(f">> Recipients: {recipients}")

        ret_encrypt = gpg.encrypt(
                file_id['data'],
                recipients=recipients,
                always_trust=always_trust
        )
        
        # Delete the downloaded keystore
        self.cleanup(zip_file_id)
        
        if ret_encrypt.ok:
            self.logger.debug(">> File encrypted")

            file_id = self.set_files([{"filename": output_name, "data": ret_encrypt.data}])
            if len(file_id) == 1:
                file_id = file_id[0]
            return {"success": True, "id": file_id}
        else:
            return {"success": False, "error": ret_encrypt.stderr}


if __name__ == "__main__":
    Gpg.run()
