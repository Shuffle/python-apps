import json
import eml_parser
import datetime

def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial

# 1. 
# "headers": {
#     "headername": ["asd"]
# }

# 2. 
# "headers": [
#     "key": "headerame",
#     "value": "headervalue"
# ]

# 3. 
# Raw headers

def parse_email_headers(email_headers):
    try:
        email_headers = bytes(email_headers,'utf-8')
        ep = eml_parser.EmlParser()
        parsed_headers = ep.decode_email_bytes(email_headers)
        return json.dumps(parsed_headers, default=json_serial)   
    except Exception as e:
        raise Exception(e)

# Basic function to check headers in an email
# Can be dumped in in pretty much any format
def analyze_headers(headers):
    # Raw
    if isinstance(headers, str):
        headers = parse_email_headers(headers)
        if isinstance(headers, str):
            headers = json.loads(headers)

        headers = headers["header"]["header"]

    # Just a way to parse out shitty email formats 
    if "header" in headers:
        headers = headers["header"]
        if "header" in headers:
            headers = headers["header"]
    
    if not isinstance(headers, list):
        newheaders = []
        for key, value in headers.items():
            if isinstance(value, list):
                newheaders.append({
                    "key": key,
                    "value": value[0],
                })
            else:
                newheaders.append({
                    "key": key,
                    "value": value,
                })

        headers = newheaders


    spf = False
    dkim = False
    dmarc = False
    spoofed = False

    analyzed_headers = {
        "success": True,
    }

    for item in headers:
        if "name" in item:
            item["key"] = item["name"]

        item["key"] = item["key"].lower()

        if "spf" in item["key"]:
            if "pass " in item["value"].lower():
                spf = True

        if "dkim" in item["key"]:
            if "pass " in item["value"].lower():
                dkim = True

        if "dmarc" in item["key"]:
            print("dmarc: ", item["key"])

        if item["key"] == "authentication-results":
            if "spf=pass" in item["value"]:
                spf = True
            if "dkim=pass" in item["value"]:
                dkim = True
            if "dmarc=pass" in item["value"]:
                dmarc = True

        # Fix spoofed!
        if item["key"] == "from":
            print("From: " + item["value"])

            if "<" in item["value"]:
                item["value"] = item["value"].split("<")[1]

            for subitem in headers:
                if "name" in subitem:
                    subitem["key"] = subitem["name"]

        
                subitem["key"] = subitem["key"].lower()
                print("Found: ", subitem["key"])

                if subitem["key"] == "reply-to":
                    if "<" in subitem["value"]:
                        subitem["value"] = subitem["value"].split("<")[1]

                    print("Reply-To: " + subitem["value"], item["value"])
                    if item["value"] != subitem["value"]:
                        spoofed = True
                        analyzed_headers["spoofed_reason"] = "Reply-To is different than From"
                        break

                if subitem["key"] == "mail-reply-to":
                    if "<" in subitem["value"]:
                        subitem["value"] = subitem["value"].split("<")[1]

                    if item["value"] != subitem["value"]:
                        spoofed = True
                        analyzed_headers["spoofed_reason"] = "Mail-Reply-To is different than From"
                        break

    analyzed_headers["spf"] = spf
    analyzed_headers["dkim"] = dkim
    analyzed_headers["dmarc"] = dmarc
    analyzed_headers["spoofed"] = spoofed

    # Should be a dictionary
    return analyzed_headers 


with open("hdr.txt", "r") as tmp:
    data = json.loads(tmp.read())
    print(analyze_headers(data))

    print()
#
#with open("hdr2.txt", "r") as tmp:
#    data = json.loads(tmp.read())
#    print(analyze_headers(data))
#
#    print()
#
#with open("hdr3.txt", "r") as tmp:
#    data = tmp.read()
#    print(analyze_headers(data))
