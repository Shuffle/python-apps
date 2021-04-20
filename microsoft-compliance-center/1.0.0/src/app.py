import socket
import asyncio
import time
import random
import json
import uuid
import time
import requests

from walkoff_app_sdk.app_base import AppBase

# Antispam
# https://protection.office.com/threatpolicy
# https://protection.office.com/antispam
# https://docs.microsoft.com/en-us/microsoft-365/security/office-365-security/configure-the-connection-filter-policy?view=o365-worldwide

#create_url = "https://compliance.microsoft.com/api/ComplianceSearch"
#Request URL: 
# https://docs.microsoft.com/en-us/information-protection/develop/overview
# https://docs.microsoft.com/en-us/graph/api/resources/ediscovery-ediscoveryapioverview?view=graph-rest-beta
# Microsoft Graph Security securityAction entity
# https://docs.microsoft.com/en-us/graph/api/resources/threatassessment-api-overview?view=graph-rest-1.0

# Permissions (Delegated): SecurityEvents, ThreatAssement, ThreatIndicators, Compliance
# !! Have a "report email" internally using office365 !! 
# Microsoft Threat Protection
# https://security.microsoft.com/mtp/
# https://protection.office.com/api/AcceptedDomain

class MSComplianceCenter(AppBase):
    __version__ = "1.0.0"
    app_name = "microsoft-compliance-center"

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    async def authenticate(self, tenant_id, client_id, client_secret, graph_url):
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

    async def block_sender_domain(self, csrf_token, session_token, domain, reporting_email):
        scc_cookie = session_token
        xsrf_token = csrf_token
        # Enable-OrganizationCustomization
    
        bearerToken = "hello"
        headers = {
            "Content-Type": "application/json",
            "X-XSRF-TOKEN": f"{xsrf_token}",
            "Cookie":  f"sccauth={scc_cookie};",
        }

        policyName = "Shuffle Block Policy"
        get_url = "https://protection.office.com/api/HostedContentFilterRule"
        ret = requests.get(get_url, headers=headers)
        print(ret.text)
        print(ret.status_code)
        #try:
        #    return ret.json()
        #except (json.JSONDecodeError, KeyError, NameError) as e:
        #    #return {"success": True, "reason": 
        #    return ret.text
        our_rule = {"name": ""}
        try:
            for rule in ret.json():
                if rule["name"] == policyName:
                    our_rule = rule
                    break
        except json.decoder.JSONDecodeError as e:
            print(f"[ERROR] Decoding {ret.text}: {e}") 
            return {
                "success": False,
                "reason": e,
            }

        blockedDomains = [{"value": domain}]
        redirectEmail = reporting_email
        data = {"blockedSenderDomains":blockedDomains,"isShowingDetails":False,"policy":{"spamAction":0,"spamQuarantineTag":"","highConfidenceSpamAction":0,"highConfidenceSpamQuarantineTag":"","markAsSpamBulkMail":1,"markAsSpamBulkMailEnabled":True,"bulkThreshold":7,"quarantineRetentionPeriod":30,"allowedSenders":[],"allowedSenderDomains":[],"blockedSenders":[],"increaseScoreWithImageLinks":0,"increaseScoreWithBizOrInfoUrls":0,"increaseScoreWithNumericIps":0,"increaseScoreWithRedirectToOtherPort":0,"markAsSpamEmptyMessages":0,"markAsSpamJavaScriptInHtml":0,"markAsSpamObjectTagsInHtml":0,"markAsSpamFramesInHtml":0,"markAsSpamEmbedTagsInHtml":0,"markAsSpamFormTagsInHtml":0,"markAsSpamWebBugsInHtml":0,"markAsSpamSensitiveWordList":0,"markAsSpamSpfRecordHardFailOn":False,"markAsSpamFromAddressAuthFailOn":False,"markAsSpamNdrBackscatterOn":False,"testModeAction":0,"testModeBccToRecipients":[],"enableEndUserSpamNotifications":False,"endUserSpamNotificationLanguage":"0","endUserSpamNotificationFrequency":3,"regionBlockList":[],"enableRegionBlockList":False,"languageBlockList":[],"enableLanguageBlockList":False,"enableSafetyTipsLite":True,"bulkSpamAction":0,"bulkQuarantineTag":"","phishSpamAction":3,"phishQuarantineTag":"","spamZapEnabled":True,"phishZapEnabled":True,"applyPhishActionToIntraOrg":False,"highConfidencePhishAction":2,"highConfidencePhishQuarantineTag":"","recommendedPolicyType":"Custom","redirectToRecipientsString":redirectEmail,"addXHeaderValue":"","modifySubjectValue":"","markAsSpamSpfRecordHardFail":0,"markAsSpamFromAddressAuthFail":0,"markAsSpamNdrBackscatter":0},"recipientDomainIs":["shufflertest2.onmicrosoft.com"],"sentTo":None,"sentToMemberOf":None,"exceptIfRecipientDomainIs":None,"exceptIfSentTo":[redirectEmail],"exceptIfSentToMemberOf":None,"name":policyName}

        if our_rule["name"] == "":
            print("Rule %s not found!" % policyName)
            our_rule = data
        else:
            print("Rule %s WAS FOUND!" % policyName)
            for item in our_rule["blockedSenderDomains"]:
                if domain in item["value"]:
                    return {"success": True, "reason": "Domain is already blocked"}

            our_rule["blockedSenderDomains"].append(domain)

        create_url = "https://protection.office.com/api/HostedContentFilterRule"
        ret = requests.post(create_url, json=our_rule, headers=headers)
        print(ret.text)
        print(ret.status_code)
        try:
            return ret.json()
        except (json.JSONDecodeError, KeyError, NameError) as e:
            #return {"success": True, "reason": 
            return ret.text


        #graph_url = "https://graph.microsoft.com"
        #session = await self.authenticate(tenant_id, client_id, client_secret, graph_url)
        #create_url = "https://protection.office.com/api/ComplianceSearch"
        #create_url = "https://compliance.microsoft.com/api/ComplianceSearch"
        ##https://protection.office.com/api/HostedContentFilterRule
        #ret = session.post(graph_url)
        #print(ret.status_code)
        #print(ret.text)
        #if ret.status_code < 300:
        #    data = ret.json()
        #    #return {"success": True, "alerts": data["value"]}

        #return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code}

        # ENABLE: https://protection.office.com/api/OrganizationCustomization/Enable?source=HostedContentFilterPolicy


        # GET:https://graph.microsoft.com/v1.0/me/messages?$filter=from/emailAddress/address+eq+'xx@xxxx.onmicrosoft.com'+and+isRead+eq+False

    async def get_alerts(self, tenant_id, client_id, client_secret):
        graph_url = "https://graph.microsoft.com"
        session = await self.authenticate(tenant_id, client_id, client_secret, graph_url)

        graph_url = "https://graph.microsoft.com/v1.0/security/alerts"
        ret = session.get(graph_url)
        print(ret.status_code)
        print(ret.text)
        if ret.status_code < 300:
            data = ret.json()
            return {"success": True, "alerts": data["value"]}

        return {"success": False, "reason": "Bad status code %d - expecting 200." % ret.status_code}
    
    async def run_content_search(self, sender_email, name, csrf_token, session_token):
        #graph_url = "https://graph.microsoft.com/v1.0/search/query"
        #incidents_url = f"{azure_url}/subscriptions/{kwargs['subscription_id']}/resourceGroups/{kwargs['resource_group_name']}/providers/Microsoft.OperationalInsights/workspaces/{kwargs['workspace_name']}/providers/Microsoft.SecurityInsights/incidents"
        #params = {"api-version": "2020-01-01"}
    
        # Request URL: https://compliance.microsoft.com/api/ComplianceSearch
    
        scc_cookie = session_token
        xsrf_token = csrf_token
    
        bearerToken = "hello"
        headers = {
            "Content-Type": "application/json",
            "X-XSRF-TOKEN": f"{xsrf_token}",
            "Cookie":  f"sccauth={scc_cookie};",
        }
        
        #eyJ0e...Qa6wg
        #"Authorization": f"Bearer {bearerToken}",
        description = ""
    
        data = {
            "identity":"",
            "name": name,
            description: description,
            "language":"",
            "contentQuery":{
                "ShouldUseRawContent":False,
                "RawContent":"",
                "Root":{
                    "$type":"Microsoft.Office.Compliance.Repository.ComplexCondition, Microsoft.Office.Compliance.Repository","Logic":"Or","Conditions":[{
                        "$type":"Microsoft.Office.Compliance.Repository.SimpleCondition, Microsoft.Office.Compliance.Repository",
                        "IsExclusive":False,
                        "IsLeaf":True,
                        "Operator":"EqualAnyof",
                        "Property":"senderauthor",
                        "Values":[sender_email],
                        "ValueType":"String"
                    }],"IsExclusive":False
                }
            },
            "includeUserAppContent":True,
            "searchAllHoldLocations":False,
            "searchAllExchange":True,
            "searchAllSharepoint":True,
            "searchAllPublicFolders":True
        }
    
        create_url = "https://compliance.microsoft.com/api/ComplianceSearch"
        #create_url = "https://protection.office.com/api/ComplianceSearch"
        ret = requests.post(create_url, json=data, headers=headers)
        print("RET CONTENT: ")
        print(ret.text)
        if ret.status_code == 200:
            print("SUCCESS: %d" % ret.status_code)
        else:
            failed = True
            if "already exists within" in ret.text:
                name = name+str(uuid.uuid4())
                data["name"] = name
                print("Failed, but added uuid to run unique search with same name. New search name: %s" % name)
    
                ret = requests.post(create_url, json=data, headers=headers)
                if ret.status_code == 200:
                    failed = False
    
            if failed:
                print("Failed: %d!" % ret.status_code)
                return {"success": False, "reason": f"Status code wasn't 200 for search creation, but {ret.status_code}"}
    
        print()
    
        time.sleep(3)
        params = {
            "id": name,
            "retry": "False",
        }
    
        print("Starting the search")
        run_url = "https://compliance.microsoft.com/api/ComplianceSearch/StartSearch"
        ret = requests.put(run_url, params=params, headers=headers)
        print("RET CONTENT: ")
        print(ret.text)
        if ret.status_code == 200:
            print("SUCCESS (2): %d" % ret.status_code)
        else:
            print("Failed (2): %d!" % ret.status_code)
            return {"success": False, "reason": f"Status code wasn't 200 for search start, but {ret.status_code}"}
    
        print()
    
        timeout = 120
        while True:
            params = {
                "id": name,
            }
    
            ret = requests.get(create_url, headers=headers, params=params)
            print(ret.text)
            if ret.status_code != 200:
                print("Not finished (3): %d" % ret.status_code)
                time.sleep(5)
                continue
    
            #print(ret.status_code)
            try:
                data = ret.json()
    
                indexed_item_count = data["indexedItemsCount"]
                item_size = data["indexedItemsSize"]
    
                print()
                jobProgress = data["jobProgress"]
                print("Items: %d, result size: %d" % (indexed_item_count, item_size))
                print("Progress: %d, status: %d" % (jobProgress, data["status"]))
    
                if jobProgress == 100:
                    print("SHOULD BREAK - HAVE RESULT!")
    
                    locations = []
                    for item in data["searchStatistics"]["ExchangeBinding"]["Sources"]:
                        try:
                            if item["ContentItems"] > 0 or item["ContentSize"] != "0 B":
                                locations.append(item)
                        except (json.JSONDecodeError, KeyError, NameError) as e:
                            print("Error for %s: %s" % (item, e))
    
                    #"sources": data["Sources"],
                    # successResults
                    return {
                        "success": True,
                        "search_name": name,
                        "result": {
                            "items": indexed_item_count,
                            "size": item_size,
                        },
                        "locations": locations,
                    }
                    break
    
                print(f"COUNT: {indexed_item_count}, Size: {item_size}")
            except (json.JSONDecodeError, KeyError, NameError) as e:
                print(f"Outer Error: {e}")
    
            time.sleep(5)
    
    #https://protection.office.com/api/ComplianceSearch/StartSearch?id=Another+search&retry=False

if __name__ == "__main__":
    asyncio.run(MSComplianceCenter.run(), debug=True)
