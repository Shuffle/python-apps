# Velociraptor
## Overview
Velociraptor is an open source, cross-platform endpoint visibility tool that allows for endpoint detection, forensics, monitoring, and response at scale.

You can read more about Velociraptor here: https://docs.velociraptor.app/

This app allows provides integration with Velociraptor's GRPC API to facilitate the automation of artifact collection and response actions to increase context and save defenders time during security operations and investigations.

## Actions
The following actions are currently available:

- Add client label
- Add client quarantine (Only Windows hosts supported at this time)
- Get client ID
- Get client flows
- Get client flow results
- Get client label
- Get hunt flows
- Get hunt results
- Remove client label
- Remove client quarantine
- Search filename (create a hunt for a particular file name)
- Search hash (create a hunt for a particular file hash)
- Search with custom query (free-form VQL query)

## Authentication

#### Create API config file
An API config file must be created for authentication to the Velociraptor API. Instructions on how to create this file can be found here:

https://docs.velociraptor.app/docs/server_automation/server_api/#creating-a-client-api-certificate

#### Upload file to Shuffle
Navigate to `ADMIN -> Files`, then upload your API config file. Make sure to copy the file ID, as you'll need it when configuring the app in the workflow
![image](https://user-images.githubusercontent.com/16829864/165663167-35c965fd-829b-497d-9265-12da98736a64.png)

#### Add Authentication in Worklow
Next, inside of a new workflow, add the Velociraptor app, then click to configure it:

![image](https://user-images.githubusercontent.com/16829864/165663321-c9760a57-1d6c-4ccc-a4f9-9c3d0ce5d289.png)


Enter a title for the authentication configuration, and paste the file ID into the `api_config` input field:

![image](https://user-images.githubusercontent.com/16829864/165663556-bd48696c-e613-4079-8feb-383012f2fa1b.png)

#### Test Authentication
To test authentication, try using the `Search with custom query` action with the following query:

`SELECT * FROM info()`

Results similar to the following should be returned:

![image](https://user-images.githubusercontent.com/16829864/165664085-ac40f855-c32b-4b18-ad90-cb1a3651ca35.png)
