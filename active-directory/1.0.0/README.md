# Intro
Active Directory is used all over the world for different reasons. This app helps you explore and control those users. It's based on an LDAP connection.

## Authentication
* server: The IP or hostname to connect to 
* port: The port to connect to. Default: 389
* domain: Your CORP domain. Used to login properly together with your login_user
* login_user: Your username. DONT add CORP\\ in front
* password: The password of the user logging in.
* base_dn: The base DN to e.g. search from or find a user from. `dsquery user USERNAME`. Should NOT contain spaces. Example: `ou=Users,ou=GPO Groups,dc=nameofdomainserver,dc=company,dc=com` 
* use_ssl: Whether to use SSL to connect to the default port.

## Typical issues
- InvalidCredentials: This happens when the credentials are wrong. 

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
