## Microsoft Compliance Center

## Register an App

### Step 1: Go to the Azure Portal

 - You'll need to go to the [Azure Portal](https://portal.azure.com/) and login.

### Step 2: Go to the Azure Active Directory Service

- Once you are logged into Azure, Register a new application so you can access
the Microsoft Graph API. To register a new application go to your **Azure Active Directory**
and once there go down to **App Registrations** a new window will pop up.

### Step 3: Register a New App
- Set name of your choice.
- Set **Supported account** types to Accounts in any organizational directory and personal Microsoft accounts.
- You don't have to set redirect URL.

### Step 4: Generate client secret
- Go to your application &#8594; Certificates & Secrets &#8594; New client Secret

## Note
- You'll need Tenant ID, Client ID & client Secret for authentication (Tenant ID & Client ID are available under application overview and for Client Secret  go to Certificate & Secrets section).
- Make sure your application has adequate permissions.
- To add permission, Go to your application &#8594; API permission &#8594; Add permission (some of the permissions will require admin consent)
- After adding permission , Grant consent.
