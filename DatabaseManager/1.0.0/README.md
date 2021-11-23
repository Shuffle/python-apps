## Database Manager
An app for interacting with databases (currently only supports MySQL). Support for more database will be added as per the requirement.

## Requirements
- Database host address
- Port number
- Username and password

## Action
1) __Query MySQL Database__
- Use this action for querying MySQL database

  __Action parameters :-__
  - __Username__ : username of database account
  - __Password__ : password of database account
  - __Host__ : database host address
  - __Port__ : Port number of database
  - __Database name__ : database name you want to use
  - __Query__ : query you want to run ( SELECT * FROM example_table; )

- You'll receive query output in json format.
