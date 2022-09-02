#!/usr/bin/env python3
import json
import ldap3
import asyncio
from ldap3 import (
    Server,
    Connection,
    MODIFY_REPLACE,
    ALL_ATTRIBUTES,
)
def __ldap_connection( server, port, domain, login_user, password, use_ssl):
    use_SSL = False if use_ssl.lower() == "false" else False
    login_dn = domain + "\\" + login_user

    s = Server(server, port=int(port), use_ssl=use_SSL)
    c = Connection(s, user=login_dn, password=password, auto_bind=True)

    return c

def __getUserAccountControlCode(input_attributes):
    userAccountControlFlags = {
        "TRUSTED_TO_AUTH_FOR_DELEGATION": 16777216,
        "PASSWORD_EXPIRED": 8388608,
        "DONT_REQ_PREAUTH": 4194304,
        "USE_DES_KEY_ONLY": 2097152,
        "NOT_DELEGATED": 1048576,
        "TRUSTED_FOR_DELEGATION": 524288,
        "SMARTCARD_REQUIRED": 262144,
        "MNS_LOGON_ACCOUNT": 131072,
        "DONT_EXPIRE_PASSWORD": 65536,
        "SERVER_TRUST_ACCOUNT": 8192,
        "WORKSTATION_TRUST_ACCOUNT": 4096,
        "INTERDOMAIN_TRUST_ACCOUNT": 2048,
        "NORMAL_ACCOUNT": 512,
        "TEMP_DUPLICATED_ACCOUNT": 256,
        "ENCRYPTED_TEXT_PWD_ALLOWED": 128,
        "PASSWD_CANT_CHANGE": 64,
        "PASSWD_NOTREQD": 32,
        "LOCKOUT": 16,
        "HOMEDIR_REQUIRED": 8,
        "ACCOUNTDISABLED": 2,
        "SCRIPT": 1,
    }
    code = 0
    for attribute in input_attributes:
        code += userAccountControlFlags[attribute]
    
    return code


# Decode UserAccountControl code
def __getUserAccountControlAttributes(input_code):
    userAccountControlFlags = {
        16777216: "TRUSTED_TO_AUTH_FOR_DELEGATION",
        8388608: "PASSWORD_EXPIRED",
        4194304: "DONT_REQ_PREAUTH",
        2097152: "USE_DES_KEY_ONLY",
        1048576: "NOT_DELEGATED",
        524288: "TRUSTED_FOR_DELEGATION",
        262144: "SMARTCARD_REQUIRED",
        131072: "MNS_LOGON_ACCOUNT",
        65536: "DONT_EXPIRE_PASSWORD",
        8192: "SERVER_TRUST_ACCOUNT",
        4096: "WORKSTATION_TRUST_ACCOUNT",
        2048: "INTERDOMAIN_TRUST_ACCOUNT",
        512: "NORMAL_ACCOUNT",
        256: "TEMP_DUPLICATED_ACCOUNT",
        128: "ENCRYPTED_TEXT_PWD_ALLOWED",
        64: "PASSWD_CANT_CHANGE",
        32: "PASSWD_NOTREQD",
        16: "LOCKOUT",
        8: "HOMEDIR_REQUIRED",
        2: "ACCOUNTDISABLED",
        1: "SCRIPT",
    }
    lists = []
    attributes = {}
    while input_code > 0:
        for flag, flagName in userAccountControlFlags.items():
            temp = input_code - flag
            if temp > 0:
    	        attributes[userAccountControlFlags[flag]] = flag
    	        input_code = temp
            if temp == 0:
    	        try:
                    if userAccountControlFlags[input_code]:
                        attributes[userAccountControlFlags[input_code]] = input_code
    	        except KeyError:
    	    	    pass
    	        input_code = temp
    for key, val in attributes.items():
        lists.append(key)
    return lists



# Disable User
def disable_user(

server,
port,
    domain,
    login_user,
    password,
    base_dn,
    use_ssl,
    samaccountname,
    search_base,
):

    if search_base:
        base_dn = search_base

    c = __ldap_connection(server, port, domain, login_user, password, use_ssl)

    result = json.loads(
        user_attributes(
            server,
            port,
            domain,
            login_user,
            password,
            base_dn,
            use_ssl,
            samaccountname,
            search_base,
        )
    )
    userAccountControl = result["attributes"]["userAccountControl"]

    if "ACCOUNTDISABLED" in userAccountControl:
        result = {}
        result["samAccountName"] = samaccountname
        result["status"] = "success"
        result["description"] = "Account already disable"

        return json.dumps(result)
    else:
        userAccountControl.append("ACCOUNTDISABLED")
        userAccountControl_code = __getUserAccountControlCode(
            userAccountControl
        )
        new_userAccountControl = {
            "userAccountControl": (MODIFY_REPLACE, userAccountControl_code)
        }
        user_dn = result["dn"]
        c.modify(dn=user_dn, changes=new_userAccountControl)
        c.result["samAccountName"] = samaccountname

        return json.dumps(c.result)

# Get User Attributes
def user_attributes(
    
    server,
    port,
    domain,
    login_user,
    password,
    base_dn,
    use_ssl,
    samaccountname,
    search_base,
):
    if search_base:
        base_dn = search_base

    c =__ldap_connection(server, port, domain, login_user, password, use_ssl)

    print(c, base_dn, samaccountname)
    c.search(
        search_base=base_dn,
        search_filter=f"(samAccountName={samaccountname})",
        attributes=ALL_ATTRIBUTES,
    )

    result = json.loads(c.response_to_json())
    print(result)
    result = result["entries"][0]
    result["attributes"]["userAccountControl"] = __getUserAccountControlAttributes(
        result["attributes"]["userAccountControl"]
    )

    return json.dumps(result)


disable_user(
    '172.17.12.5',
    389,
    'ICPLAHD',
    'administrator',
    'PW',
    'CN=Users,DC=icplahd,DC=local',
    'false',
    'administrator',
    'CN=Users,DC=icplahd,DC=local',
)
