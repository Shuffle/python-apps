import tempfile
import requests
import zipfile
import gnupg
import os

file_id = ""

def get_file(value):
    url = "https://shuffler.io"
    authorization = ""
    full_execution = {
        "execution_id": "1234",
        "authorization": "",
        "workflow": {
            "execution_org": {
                "id": "",
            }
        }
    }

    full_execution = full_execution
    org_id = full_execution["workflow"]["execution_org"]["id"]

    #logger.info("SHOULD GET FILES BASED ON ORG %s, workflow %s and value(s) %s" % (org_id, full_execution["workflow"]["id"], value))

    if isinstance(value, list):
        pass
        #self.logger.info("IS LIST!")
        #if len(value) == 1:
        #    value = value[0]
    else:
        value = [value]

    returns = []
    for item in value:
        #self.logger.info("VALUE: %s" % item)
        if len(item) != 36 and not item.startswith("file_"):
            #self.logger.info("Bad length for file value %s" % item)
            continue
            #return {
            #    "filename": "",
            #    "data": "",
            #    "success": False,
            #}

        get_path = "/api/v1/files/%s?execution_id=%s" % (item, full_execution["execution_id"])
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % authorization
        }

        ret1 = requests.get("%s%s" % (url, get_path), headers=headers)
        if ret1.status_code != 200:
            returns.append({
                "filename": "",
                "data": "",
                "success": False,
            })
            continue

        content_path = "/api/v1/files/%s/content?execution_id=%s" % (item, full_execution["execution_id"])
        ret2 = requests.get("%s%s" % (url, content_path), headers=headers)
        if ret2.status_code == 200:
            tmpdata = ret1.json()
            returndata = {
                "success": True,
                "filename": tmpdata["filename"],
                "data": ret2.content,
            }
            returns.append(returndata)


    if len(returns) == 0:
        return {
            "success": False,
            "filename": "",
            "data": b"",
        }
    elif len(returns) == 1:
        return returns[0]
    else:
        return returns

def get_auth(file_id):
    item = get_file(file_id)
    tmpdirname = "/tmp/%s" % file_id
    if not os.path.exists(tmpdirname):
        os.mkdir(tmpdirname)

    #with tempfile.TemporaryDirectory() as tmpdirname:
    # Get archive and save phisically
    with open(os.path.join(tmpdirname, "archive"), "wb") as f:
        f.write(item["data"])

    # Grab files before, upload them later
    gpgfound = False
    with zipfile.ZipFile(os.path.join(tmpdirname, "archive")) as z_file:
        print("Past zip extraction")
        for member in z_file.namelist():
            print(member)
            if member == ".gpg":
                gpgfound = True 

            z_file.extract(member, tmpdirname)

    os.remove(os.path.join(tmpdirname, "archive"))

    if gpgfound: 
        tmpdirname = os.path.join(tmpdirname, ".gpg")

    try:
        gpg = gnupg.GPG(gnupghome=tmpdirname)
    except TypeError:
        gpg = gnupg.GPG(homedir=tmpdirname)

    return gpg

get_auth(file_id)
