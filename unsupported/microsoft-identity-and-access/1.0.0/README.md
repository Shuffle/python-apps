## Microsoft Identity and Access
- An app to interact with Active Directory in Azure.

**PS: If you want to Reset a password in Azure AD, please use the "Azure AD Delegated" app, and use ONLY delegated permissions for this.** 

## How to register app in Active Directory on Azure portal?

### Step 1: Go to the Azure portal

 - You'll need to go to the [Azure Portal](https://portal.azure.com/) and login.

### Step 2: Go to the Azure Active Directory Service

- Once you are logged into Azure, Register a new application so you can access
the Microsoft Graph API. To register a new application go to your **Azure Active Directory**
and once there go down to **App Registrations** a new window will pop up.

### Step 3: Register a New App
- Set name of your choice.
- Select supported account type.
- You don't have to set redirect URL.

### Step 4: Generate client secret
- Go to your application &#8594; Certificates & Secrets &#8594; New client Secret.

## Note
- You'll need Tenant ID, Client ID & client Secret for authentication (Tenant ID & Client ID are available under application overview and for Client Secret  go to Certificate & Secrets section).
- Make sure your application has adequate permissions.
- Each action may require different permission to run. To add permissions, Go to your application in azure portal &#8594; API permission &#8594; Add permission (some of the permissions will require admin consent).
- After adding permission , Grant consent.
- Some of the actions are not supported on personal account.


## References
- To read more about required permission for each action you can refer to [Identity & Access](https://docs.microsoft.com/en-us/graph/api/resources/azure-ad-overview?view=graph-rest-1.0)'s official documentation.
