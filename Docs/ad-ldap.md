# AD LDAP App

The AD LDAP app is used to query Active Directory and/or LDAP for associated attributes. Currently, this is focused on Active Directory and can query by SamAccountName but more functionality to come!

![image](https://user-images.githubusercontent.com/11653079/113415296-e57fe200-938c-11eb-8303-149cb9f85f50.png)

## Actions

- Search samaccountname

## Requirements

- Active Directory account with permissions to BIND and lookup user attributes

## Setup

1. Collect details for the Active Directory user that will be used to query AD/LDAP
2. Add the `AD LDAP` node to your workflow
3. Enter the required parameters:
    - **domain_name**: "CONTOSO"
    - **server_name**: "dc.contoso.com"
    - **user_name**: "binduser"
    - **password**: "Password123IsWeak"
    - **samaccountname**: "smithj"
    - **search_base**: "OU=users,DC=contoso,DC=local"
    - **port**: 3269 (AD Global Catalog SSL port)
    - **use_ssl**: true
