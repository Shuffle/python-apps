## PagerDuty App

- The PagerDuty app for creating and managing incident from shuffle.

## Actions

1. List all incidents
2. Get incident details
3. Get past incidents
4. Create incdent
5. Update incident status
6. Create incident note

## Requirements

- PagerDuty account
- API key 

- To generate API key, 
1. Login to your account, go to Apps & Add-Ons &#8594; API Access and click Create New API Key.
2. Enter a Description that will help you identify the key later on.
3. Click Create Key.
4. A unique API key will be generated. Copy it to a safe place, as you will not have access to copy this key again. Once it has been copied, click Close. If you lose a key you will need to delete it and create a new one.

## Setup

#### Authentication

- Add your API key in api_key field.
- Some action needs API key as well as email of the user (Make sure email and API key belongs to the same user).

## Note

##### How to find service id ?
- Login to your PagerDuty account, Go to Services &#8594; Service Directory &#8594; select your desired service.
- Now look at url of the page, It'll be like this https://your-domain.pagerduty.com/service-directory/{your-service-id}

##### How to find incident id ?
- Login to your PagerDuty account, Go to Incidents &#8594; All Incidents &#8594; select your desired incident.
- Now look at url of the page, It'll be like this https://your-domain.pagerduty.com/Incidents/{your-incident-id}
