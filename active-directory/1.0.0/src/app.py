import json
import ldap3
import asyncio
from ldap3 import (
    Server,
    Connection,
    MODIFY_REPLACE,
    ALL_ATTRIBUTES,
)
from ldap3.extend.microsoft.addMembersToGroups import ad_add_members_to_groups as addUsersInGroups
from ldap3.extend.microsoft.removeMembersFromGroups import ad_remove_members_from_groups as removeUsersFromGroups

from walkoff_app_sdk.app_base import AppBase

class ActiveDirectory(AppBase):
    __version__ = "1.0.1"
    app_name = "Active Directory"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    def __ldap_connection(self, server, port, domain, login_user, password, use_ssl):
        use_SSL = False if use_ssl.lower() == "false" else False
        login_dn = domain + "\\" + login_user

        s = Server(server, port=int(port), use_ssl=use_SSL)
        c = Connection(s, user=login_dn, password=password, auto_bind=True)

        return c

    # Decode UserAccountControl code
    def __getUserAccountControlAttributes(self, input_code):
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

    # Encode UserAccountControl attributes
    def __getUserAccountControlCode(self, input_attributes):
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

    # Get User Attributes
    def user_attributes(
        self,
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

        c = self.__ldap_connection(server, port, domain, login_user, password, use_ssl)

        try:
            c.search(
                search_base=base_dn,
                search_filter=f"(samAccountName={samaccountname})",
                attributes=ALL_ATTRIBUTES,
            )

            result = json.loads(c.response_to_json())
            if len(result["entries"]) == 0:
                return json.dumps({
                    "success": False,
                    "result": result, 
                    "reason": "No user found for %s" % samaccountname,
                })

        except Exception as e:
            return json.dumps({
                "success": False,
                "reason": "Failed to get users in user attributes: %s" % e,
            })


        result = result["entries"][0]
        result["attributes"]["userAccountControl"] = self.__getUserAccountControlAttributes(result["attributes"]["userAccountControl"])

        return json.dumps(result)

    # Change User Password
    def set_password(
        self,
        server,
        port,
        domain,
        login_user,
        password,
        base_dn,
        use_ssl,
        samaccountname,
        new_password,
        repeat_password,
        search_base,
    ):
        if search_base:
            base_dn = search_base

        if new_password != repeat_password:
            return "Password does not match!"
        else:
            c = self.__ldap_connection(
                server, port, domain, login_user, password, use_ssl
            )

            result = json.loads( self.user_attributes( server, port, domain, login_user, password, base_dn, use_ssl, samaccountname, search_base,))

            user_dn = result["dn"]
            c.extend.microsoft.modify_password(user_dn, new_password)

            return json.dumps(c.result)

    # Change User Password at Next Logon
    def change_password_at_next_logon(
        self,
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

        c = self.__ldap_connection(server, port, domain, login_user, password, use_ssl)

        result = json.loads(
            self.user_attributes(
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

        if "DONT_EXPIRE_PASSWORD" in userAccountControl:
            return "Error: Flag DONT_EXPIRE_PASSWORD is set."
        else:
            user_dn = result["dn"]
            password_expire = {"pwdLastSet": (MODIFY_REPLACE, [0])}
            c.modify(dn=user_dn, changes=password_expire)
            c.result["samAccountName"] = samaccountname

            return json.dumps(c.result)

    # Enable User
    def enable_user(
        self,
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

        c = self.__ldap_connection(server, port, domain, login_user, password, use_ssl)

        result = json.loads(
            self.user_attributes(
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
            userAccountControl.remove("ACCOUNTDISABLED")
            userAccountControl_code = self.__getUserAccountControlCode(
                userAccountControl
            )
            new_userAccountControl = {
                "userAccountControl": (MODIFY_REPLACE, userAccountControl_code)
            }
            user_dn = result["dn"]
            c.modify(dn=user_dn, changes=new_userAccountControl)
            c.result["samAccountName"] = samaccountname

            return json.dumps(c.result)
        else:
            result = {}
            result["samAccountName"] = samaccountname
            result["status"] = "success"
            result["description"] = "Account already enable"

            return json.dumps(result)

    # Disable User
    def disable_user(
        self,
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

        c = self.__ldap_connection(server, port, domain, login_user, password, use_ssl)

        result = json.loads(
            self.user_attributes(
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

        try:
            userAccountControl = result["attributes"]["userAccountControl"]
        except Exception as e:
            return {
                "success": False,
                "reason": "Failed to get result attributes: %s" % e,
            }
            

        if "ACCOUNTDISABLED" in userAccountControl:
            try:
                result = {}
                result["samAccountName"] = samaccountname
                result["status"] = "success"
                result["description"] = "Account already disable"
                result["success"] = True

                return json.dumps(result)
            except Exception as e:
                return {
                    "success": False,
                    "reason": "Failed to send baseresult in disable user: %s" % e,
                }
        else:
            try:
                userAccountControl.append("ACCOUNTDISABLED")
                userAccountControl_code = self.__getUserAccountControlCode(
                    userAccountControl
                )
                new_userAccountControl = {
                    "userAccountControl": (MODIFY_REPLACE, userAccountControl_code)
                }
                user_dn = result["dn"]
                c.modify(dn=user_dn, changes=new_userAccountControl)
                c.result["samAccountName"] = samaccountname

                return json.dumps(c.result)
            except Exception as e:
                return {
                    "success": False,
                    "reason": "Failed adding ACCOUNTDISABLED to user: %s" % e,
                }

    def lock_user(self,server,domain,port,login_user,password,base_dn,use_ssl,samaccountname,search_base):
        
        if search_base:
            base_dn = search_base

        c = self.__ldap_connection(server, port, domain, login_user, password, use_ssl)

        c.search(base_dn, f"(SAMAccountName={samaccountname})")

        if len(c.entries) == 0:
            return {"success":"false","message":f"User {samaccountname} not found"}

        user_dn = c.entries[0].entry_dn

        c.modify(user_dn, {'userAccountControl':[(MODIFY_REPLACE,[514])]})

        result = c.result
        result["success"] = True

        return result
    
    def unlock_user(self,server,domain,port,login_user,password,base_dn,use_ssl,samaccountname,search_base):
        
        if search_base:
            base_dn = search_base

        c = self.__ldap_connection(server, port, domain, login_user, password, use_ssl)

        c.search(base_dn, f"(SAMAccountName={samaccountname})")

        if len(c.entries) == 0:
            return {"success":"false","message":f"User {samaccountname} not found"}

        user_dn = c.entries[0].entry_dn

        c.modify(user_dn, {'userAccountControl':[(MODIFY_REPLACE,[0])]})

        result = c.result
        result["success"] = True

        return result
    
    def change_user_password_at_next_login(self,server,domain,port,login_user,password,base_dn,use_ssl,samaccountname,search_base,new_user_password,repeat_new_user_password):
        
        if search_base:
            base_dn = search_base

        if str(new_user_password) != str(repeat_new_user_password):
            return {"success":"false","message":"new_user_password and repeat_new_user_password does not match."}

        c = self.__ldap_connection(server, port, domain, login_user, password, use_ssl)

        c.search(base_dn, f"(SAMAccountName={samaccountname})")

        if len(c.entries) == 0:
            return {"success":"false","message":f"User {samaccountname} not found"}

        user_dn = c.entries[0].entry_dn

        c.modify(user_dn, {'pwdLastSet':(MODIFY_REPLACE, [0])})
        c.extend.microsoft.modify_password(user_dn, new_user_password.encode('utf-16-le'))

        result = c.result
        result["success"] = True

        return result

    def add_user_to_group(self, server, domain, port, login_user, password, base_dn, use_ssl, samaccountname, search_base, group_name):
        
        if search_base:
            base_dn = search_base

        c = self.__ldap_connection(server, port, domain, login_user, password, use_ssl)

        c.search(base_dn, f"(SAMAccountName={samaccountname})")
        if len(c.entries) == 0:
            return {"success":"false","message":f"User {samaccountname} not found"}
        user_dn = c.entries[0].entry_dn

        search_filter = f'(&(objectClass=group)(cn={group_name}))'
        c.search(base_dn, search_filter, attributes=["distinguishedName"])
        if len(c.entries) == 0:
            return {"success":"false","message":f"Group {group_name} not found"}
        group_dn = c.entries[0]["distinguishedName"]
        print(group_dn)

        res = addUsersInGroups(c, user_dn, str(group_dn),fix=True)
        if res == True:
            return {"success":"true","message":f"User {samaccountname} was added to group {group_name}"}
        else:
            return {"success":"false","message":f"Could not add user to group"}

    def remove_user_from_group(self, server, domain, port, login_user, password, base_dn, use_ssl, samaccountname, search_base, group_name):
        
        if search_base:
            base_dn = search_base

        c = self.__ldap_connection(server, port, domain, login_user, password, use_ssl)

        c.search(base_dn, f"(SAMAccountName={samaccountname})")
        if len(c.entries) == 0:
            return {"success":"false","message":f"User {samaccountname} not found"}
        user_dn = c.entries[0].entry_dn

        search_filter = f'(&(objectClass=group)(cn={group_name}))'
        c.search(base_dn, search_filter, attributes=["distinguishedName"])
        if len(c.entries) == 0:
            return {"success":"false","message":f"Group {group_name} not found"}
        group_dn = c.entries[0]["distinguishedName"]
        print(group_dn)

        res = removeUsersFromGroups(c, user_dn, str(group_dn),fix=True)
        if res == True:
            return {"success":"true","message":f"User {samaccountname} was removed from group {group_name}"}
        else:
            return {"success":"false","message":f"Could not remove user to group"}


if __name__ == "__main__":
    ActiveDirectory.run()
