# VulnDB App

The VulnDB app for accessing their API to get latest vulnerability notifications or metadata about vendors and products. A subscription is needed to access this service. For more details see their [webpage](https://vulndb.cyberriskanalytics.com/).

Once logged in, the [API documentation](https://vulndb.cyberriskanalytics.com/documentation/api) is available this app is based upon.

## Actions

- **Latest 20 vulns**<br>Returns the 20 most recent vulnerabilities as a JSON
object. Needs no parameters besides authentication parameters ClientID and
ClientSecret.

## Requirements

- You need an account for accessing the VulnDB database.

## Setup

1. Go to the VulnDB [API overview page](https://vulndb.cyberriskanalytics.com/oauth_clients).
1. Hit **Register new application** at the bottom of the page (under OAuth Client Applications).
1. Enter a name and an URL (URL isn't used and doesn't matter).
1. You will get a **Client ID** and a **Client Secret** which you need to give
to the VulnDB app in Shuffle as parameters.
