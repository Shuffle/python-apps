# AWS Lambda
Amazon Web Services Serverless Compute service (lambda)
## Actions

| No. | Action | Description | Parameters |
|-----|--------|-------------|------------|
|1 | List Functions | Returns a list of your Lambda functions. | access_key, secret_key, region
|2 | Get Function | Returns information about the function or function version, with a link to download the deployment package that's valid for 10 minutes. If you specify a function version, only details that are specific to that version are returned. | access_key, secret_key, region, **function_name**, qualifier
|3 | List Aliases | Returns list of aliases created for a Lambda function. | access_key, secret_key, region, **function_name**, function_version
|4 | Invoke | Invokes a Lambda function. | access_key, secret_key, region, **function_name**, invocation_type, logtype
|5 | Get Account Settings | Retrieves details about your account's limits and usage in an AWS Region.  | access_key, secret_key, region
|6 | Delete Function | Deletes a Lambda function. To delete a specific version, use the Qualifier parameter. | access_key, secret_key, region, **function_name**, qualifier
__Note__:
- access_key, secret_key and region are used for authentication.
- **Bold** Parameters are compulsory required.


## Requirements
1. AWS account
2. Access key, Secret key and region of the user.
- __How to find access key & secret key ?__
1. Open https://console.aws.amazon.com/
2. From navbar click on user dropwodown &#8594; My Security Credentials.
3. Open the Access keys tab, and then choose Create access key.
4. To see the new access key, choose Show. Your credentials resemble the following:
- Access key ID: AKIAIOSBODNN7EXAMPLE
- Secret access key: wJalrDTtnFEMI/K7MDENG/bGdRfiCYEXAMPLEKEY
Required AWS IAM Permissions and Roles for Lambda are documented here.
