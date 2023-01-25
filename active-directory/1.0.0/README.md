# Active Directory 
Active Directory is used all over the world for different reasons. This app helps you explore and control those users. It's based on an LDAP connection.

## Authentication
* server: The IP or hostname to connect to 
* port: The port to connect to. Default: 389
* domain: Your CORP domain. Used to login properly together with your login_user
* login_user: Your username. DONT add CORP\\ in front
* password: The password of the user logging in.
* base_dn: The base DN found by running `Get-ADDomain` in powershell, then getting the value of the field "UsersContainer". Should NOT contain spaces. example: `OU=Users,DC=icplahd,DC=com`
* use_ssl: Whether to use SSL to connect to the default port.

* search_base: Usually same as base_dn

## Base DN
Finding the Base DN can be done by going to a Windows server in the domain.

1. Open Powershell
2. Run
```
Get-ADDomain
```
3. Find the response from "UsersContainer" and use this for Base DN and Search Base

## Typical issues
- InvalidCredentials: This happens when the credentials are wrong. See #authentication to understand if your format for your username/password is correct.

## Features
get user attributes -- done
reset password -- done
change password at next logon -- done
enable/disable user -- done


## Upcoming Features
add/remove users to group -- dev
get group attributes -- dev
get group members -- dev
get system attributes -- dev
set system attributes -- dev
change computer OU -- dev
Connect to LDAPs using certificates and TLS
