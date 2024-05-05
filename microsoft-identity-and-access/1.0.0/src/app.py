import socket
import asyncio
import time
import random
import json
import uuid
import time
import requests

from walkoff_app_sdk.app_base import AppBase

class MsIdentityAccess(AppBase):
    __version__ = "1.0.0"
    app_name = "Microsoft Identity and Access"

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    def authenticate(self, tenant_id, client_id, client_secret, graph_url):
        s = requests.Session()
        auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": f"{graph_url}/.default",
        }
        auth_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "cache-control": "no-cache",
        }

        print(f"Making request to: {auth_url}")
        res = s.post(auth_url, data=auth_data, headers=auth_headers)

        # Auth failed, raise exception with the response
        if res.status_code != 200:
            raise ConnectionError(res.text)

        access_token = res.json().get("access_token")
        s.headers = {"Authorization": f"Bearer {access_token}", "cache-control": "no-cache"}
        return s

    # Disable = reset password & sessions
    def list_deleted_users(self, tenant_id, client_id, client_secret, user_email_or_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)


        graph_url = f"https://graph.microsoft.com/v1.0/directory/deletedItems/microsoft.graph.user"
        headers = {
            "Content-type": "application/json"
        }
        ret = session.get(graph_url, headers=headers)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code}

    # Disable = reset password & sessions
    def restore_deleted_user(self, tenant_id, client_id, client_secret, user_email_or_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/v1.0/directory/deletedItems/{user_email_or_id}/restore"
        headers = {
            "Content-type": "application/json"
        }
        ret = session.post(graph_url, headers=headers)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code}

    # Disable = reset password & sessions
    def logout_user(self, tenant_id, client_id, client_secret, user_email_or_id):

        new_password = str(uuid.uuid4())
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/v1.0/users/{user_email_or_id}/revokeSignInSessions"
        headers = {
            "Content-type": "application/json"
        }
        ret = session.post(graph_url, headers=headers)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code}

    # Disable = reset password & sessions
    def disable_user(self, tenant_id, client_id, client_secret, user_email_or_id):

        new_password = str(uuid.uuid4())
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/v1.0/users/{user_email_or_id}/revokeSignInSessions"
        headers = {
            "Content-type": "application/json"
        }
        ret = session.get(graph_url, headers=headers)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code >= 300:
            data = ret.json()
            return data

        graph_url = f"https://graph.microsoft.com/v1.0/users/{user_email_or_id}/authentication/passwordMethods"

        ret = session.get(graph_url)
        retdata = ret.json()
        #return retdata
        try:
            if len(retdata["value"]) == 0:
                return {"success": False, "reason": "Couldn't find any password methods to reset password, but DID revoke their sessions"}
        except:
            return {"success": False, "reason": "Couldn't find any password methods to reset password, but DID revoke their sessions (2)"}

        registered_password_id = retdata["value"][0]["id"]
        graph_url = f"https://graph.microsoft.com/v1.0/users/{user_email_or_id}/authentication/passwordMethods/{registered_password_id}/resetPassword"
        headers = {
            "Content-type": "application/json"
        }

        request_body = {
            "newPassword": str(new_password)
        }


        ret = session.post(graph_url, json=request_body,headers=headers)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code >= 300:
            data = ret.json()
            return data

        return {"success": True, "reason": "Stopped all active sessions and reset their password."}

    def get_user(self, tenant_id, client_id, client_secret, user_id, selected_fields=""):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = "https://graph.microsoft.com/v1.0/users?$filter=id eq '%s'" % user_id
        if len(selected_fields) > 0:
            graph_url += "&$select=%s" % selected_fields

        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code}

    def list_users(self, tenant_id, client_id, client_secret):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = "https://graph.microsoft.com/v1.0/users"
        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code}

    def list_groups(self, tenant_id, client_id, client_secret):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = "https://graph.microsoft.com/v1.0/groups"
        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code}

    def list_group_members(self, tenant_id, client_id, client_secret, group_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = "https://graph.microsoft.com/v1.0/groups/%s/members" % group_id

        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code}

    def list_administrative_units(self, tenant_id, client_id, client_secret):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = "https://graph.microsoft.com/v1.0/directory/administrativeUnits"
        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code}

    
    def get_administrative_units(self, tenant_id, client_id, client_secret,id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/v1.0/directory/administrativeUnits/{id}"
        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}

    def create_administrative_unit(self, tenant_id, client_id, client_secret, display_name, description, visibility):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/v1.0/directory/administrativeUnits"
        
        request_body = {
            "displayName": display_name,
            "description": description,
            "visibility": visibility
        }

        ret = session.post(graph_url, json= request_body)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text, "error_response":ret.text}

    def list_administrative_unit_members(self, tenant_id, client_id, client_secret,administrative_unit_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/v1.0/directory/administrativeUnits/{administrative_unit_id}/members"
        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code}

    def get_administrative_unit_member(self, tenant_id, client_id, client_secret, administrative_unit_id, member_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/v1.0/directory/administrativeUnits/{administrative_unit_id}/members/{member_id}"
        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}
    
        ## add member
    def remove_administrative_unit_member(self, tenant_id, client_id, client_secret, administrative_unit_id, user_or_group_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/v1.0/directory/administrativeUnits/{administrative_unit_id}/members/{user_or_group_id}/$ref"
        ret = session.delete(graph_url)
        print(ret.status_code)
        print(ret.text)
        return ret.json() 

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code,"error_response":ret.text}

    def list_risky_users(self, tenant_id, client_id, client_secret, amount=50, skip=0):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)
        if amount == 0 or amount == "":
            amount = 50 

        if skip == 0 or skip == "":
            skip = 0

        #graph_url = f"https://graph.microsoft.com/v1.0/identityProtection/riskyUsers?$top=%d&$skip=%d" % (int(amount), int(skip))
        graph_url = f"https://graph.microsoft.com/v1.0/identityProtection/riskyUsers?$top=%d" % (int(amount))
        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code}

    def get_risky_user(self, tenant_id, client_id, client_secret, risky_user_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/v1.0/identityProtection/riskyUsers/{risky_user_id}"
        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}

    def confirm_compromised_users(self, tenant_id, client_id, client_secret, risky_user_ids):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = "https://graph.microsoft.com/v1.0/identityProtection/riskyUsers/confirmCompromised"

        user_list = [str(user) for user in risky_user_ids.split(',')]
        
        request_body = {
            "userIds": user_list
        }
        
        ret = session.post(graph_url, json= request_body)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}

    def dismiss_compromised_users(self, tenant_id, client_id, client_secret, risky_user_ids):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = "https://graph.microsoft.com/v1.0/identityProtection/riskyUsers/dismiss"

        user_list = [str(user) for user in risky_user_ids.split(',')]
        
        request_body = {
            "userIds": user_list
        }
        
        ret = session.post(graph_url, json= request_body)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}            

    def list_directory_role(self, tenant_id, client_id, client_secret):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = "https://graph.microsoft.com/v1.0/directoryRoles"
        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}

    def list_directory_role_members(self, tenant_id, client_id, client_secret, directory_role_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/v1.0/directoryRoles/{directory_role_id}/members"
        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}    

    def add_directory_role_members(self, tenant_id, client_id, client_secret, directory_role_id, user_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/v1.0/directoryRoles/{directory_role_id}/members/$ref"

        request_body = {
            "@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"
        }

        ret = session.post(graph_url, json=request_body)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}

    def remove_directory_role_members(self, tenant_id, client_id, client_secret, directory_role_id, user_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/v1.0/directoryRoles/{directory_role_id}/members/$ref"

        request_body = {
            "@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"
        }

        ret = session.delete(graph_url, json=request_body)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}

    def delete_user(self, tenant_id, client_id, client_secret, user_email_or_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/v1.0/users/{user_email_or_id}"

        ret = session.delete(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}

    def list_password_methods(self, tenant_id, client_id, client_secret, user_email_or_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/beta/users/{user_email_or_id}/authentication/passwordMethods"

        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}
    
    def reset_user_password(self, tenant_id, client_id, client_secret, user_email_or_id , registered_password_id, new_password):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/beta/users/{user_email_or_id}/authentication/passwordMethods/{registered_password_id}/resetPassword"

        headers = {
            "Content-type": "application/json"
        }
        request_body = {
            "newPassword": str(new_password)
        }

        ret = session.post(graph_url, json=request_body,headers=headers)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}        

    def disable_user_account(self, tenant_id, client_id, client_secret, user_email_or_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/beta/users/{user_email_or_id}"

        headers = {
            "Content-type": "application/json"
        }
        request_body = {
            "accountEnabled": "False"
        }

        ret = session.patch(graph_url, json=request_body,headers=headers)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}             

    def update_user_job_title(self, tenant_id, client_id, client_secret, user_email_or_id, user_job_title):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/beta/users/{user_email_or_id}"

        headers = {
            "Content-type": "application/json"
        }
        request_body = {
            "jobTitle": user_job_title
        }

        ret = session.patch(graph_url, json=request_body,headers=headers)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}

    def update_user_department(self, tenant_id, client_id, client_secret, user_email_or_id, user_department):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/beta/users/{user_email_or_id}"

        headers = {
            "Content-type": "application/json"
        }
        request_body = {
            "department": user_department
        }

        ret = session.patch(graph_url, json=request_body,headers=headers)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}

    def update_user_employee_type(self, tenant_id, client_id, client_secret, user_email_or_id, user_employee_type):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/beta/users/{user_email_or_id}"

        headers = {
            "Content-type": "application/json"
        }
        request_body = {
            "employeeType": user_employee_type
        }

        ret = session.patch(graph_url, json=request_body,headers=headers)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}
    
    def update_user_leave_date(self, tenant_id, client_id, client_secret, user_email_or_id, user_leave_date):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/beta/users/{user_email_or_id}"

        headers = {
            "Content-type": "application/json"
        }
        request_body = {
            "employeeLeaveDateTime": user_leave_date
        }

        ret = session.patch(graph_url, json=request_body,headers=headers)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}
    
    def get_user_direct_groups(self, tenant_id, client_id, client_secret, user_email_or_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/beta/users/{user_email_or_id}/memberOf?$filter=NOT(groupTypes/any(c:c eq 'DynamicMembership'))&$count=true"

        headers = {
            "ConsistencyType": "eventual"
        }

        ret = session.get(graph_url,headers=headers)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}

    def remove_user_from_group(self, tenant_id, client_id, client_secret, user_id, group_id):
        graph_url = "https://graph.microsoft.com"
        session = self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = f"https://graph.microsoft.com/beta/groups/{group_id}/members/{user_id}/$ref"

        ret = session.delete(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return data

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code, "error_response":ret.text}

if __name__ == "__main__":
    MsIdentityAccess.run()
