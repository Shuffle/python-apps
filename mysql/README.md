MySQL/MariaDB App
---

**Index:**
[TOC]


## Create database
#### Method 1 - Create database only
For that you just need to fill the **name** and leave the **tables** field empty

#### Method 2 - Create database with tables
In order to create a new database and the tables too, you will need to fill both fields **name** and **tables**. To see how to fill the tables field check [here](#create-table/s).

## Create table/s
#### Method 1 - Create single table
```
{
    "employees": "CREATE TABLE `employees` (  `emp_no` int(11) NOT NULL AUTO_INCREMENT, `first_name` varchar(14) NOT NULL,  `last_name` varchar(16) NOT NULL,  PRIMARY KEY (`emp_no`)) ENGINE=InnoDB"
}
```
#### Method 2 - Create multiple tables
```
{
    "employees": "CREATE TABLE `employees` (  `emp_no` int(11) NOT NULL AUTO_INCREMENT, `first_name` varchar(14) NOT NULL,  `last_name` varchar(16) NOT NULL,  PRIMARY KEY (`emp_no`)) ENGINE=InnoDB",
    "departments": "CREATE TABLE `departments` (  `dept_no` char(4) NOT NULL,  `dept_name` varchar(40) NOT NULL,  PRIMARY KEY (`dept_no`), UNIQUE KEY `dept_name` (`dept_name`)) ENGINE=InnoDB"
}
```


## Insert data
#### Method 1 - Insert single row
```
{
    "title": "New Function",
    "text": "testing",
    "time": 1617032159000
}
```
OR
```
[{
    "title": "New Function",
    "text": "testing",
    "time": 1617032159000
}]
```
#### Method 2 - Insert multiple rows
```
[{
    "title": "New Function1",
    "text": "testing",
    "time": 1617032159000
},
{
    "title": "New Function2",
    "text": "testing",
    "time": 1617032159000
}]
```


## Query data
**Fields**
```
username, fname, lname
```

**Condition**
```
id=123 and gender='M'
```


## Soon
- Drop database
- Delete table
- Delete row
