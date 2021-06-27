import asyncio
import json
import mysql.connector
from mysql.connector import errorcode

# import mysql.connector

from walkoff_app_sdk.app_base import AppBase


class MySQL(AppBase):
    __version__ = "1.0.0"
    app_name = "MySQL"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    # Create Database
    async def create_database(self, server, user, password, database=None, name=None, tables=None):
        conn = mysql.connector.connect(
            host=server, user=user, passwd=password)
        cursor = conn.cursor()

        # try to create the database
        try:
            cursor.execute(
                f"CREATE DATABASE {name} DEFAULT CHARACTER SET 'utf8'")
        except mysql.connector.Error as err:
            return f"Failed creating database: {err}"

        # Try to use the database, if it does not exist it creates
        try:
            cursor.execute(f"USE {name}")
        except mysql.connector.Error as err:
            print(f"Database {name} does not exists.")
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                await self.create_database(cursor)
                print(f"Database {name} created successfully.")
                conn.database = name
            else:
                return err
        else:
            if tables:
                tables = json.loads(tables)
                t_count = 0
                for table_name in tables:
                    table_description = tables[table_name]
                    try:
                        print(f"Creating table {table_name}: ", end='')
                        cursor.execute(table_description)
                        print("created with success!")
                        t_count += 1
                    except mysql.connector.Error as err:
                        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                            print("already exists.")
                            return "already exists."
                        else:
                            print(err.msg)
                            return err.msg

                response = {
                    "message": f"Database {name} and tables created with success!",
                    "tables": tables
                }

                return json.dumps(response, indent=4)
            else:
                return f"Database {name} created with success!"

    # Create Tables
    async def create_tables(self, server, user, password, database, tables):
        tables = json.loads(tables)

        try:
            conn = mysql.connector.connect(
                host=server, user=user, passwd=password, db=database)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
                return "Something is wrong with your user name or password"
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                return "Database does not exist"
            else:
                print(err)
                return err
        else:
            cursor = conn.cursor()
            t_count = 0
            for table_name in tables:
                table_description = tables[table_name]
                try:
                    print(f"Creating table {table_name}: ", end='')
                    cursor.execute(table_description)
                    print("created with success!")
                    t_count += 1
                except mysql.connector.Error as err:
                    if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                        print("already exists.")
                        return "already exists."
                    else:
                        print(err.msg)
                        return err.msg
            result = "Table(s) created with success!" if t_count > 1 else "Table created with success!"
            return result

            cursor.close()
            conn.close()

    # Insert data into table
    async def insert_data(self, server, user, password, database, table, data):
        data = json.loads(data)

        try:
            conn = mysql.connector.connect(
                host=server, user=user, passwd=password, db=database)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
                return "Something is wrong with your user name or password"
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                return "Database does not exist"
            else:
                print(err)
                return err
        else:
            cursor = conn.cursor()
            if isinstance(data, list):
                for row in data:
                    fields = ""
                    value_fields = ""

                    if len([*row]) > 1:
                        fields = ", ".join(row.keys())
                        for i, key in enumerate(row.keys()):
                            value_fields += f"%({key})s, " if i != len(row.keys()
                                                                       ) - 1 else f"%({key})s"
                    else:
                        fields = next(iter(row.keys()))

                    sql = "INSERT INTO `" + table + \
                        "` (" + fields + ") VALUES (" + value_fields + ")"

                    try:
                        print(f"Inserting data into {table}: ", end='')
                        cursor.execute(sql, row)
                        print("inserted with success!")
                        conn.commit()
                    except mysql.connector.Error as err:
                        print(err)
                        return err
            else:
                fields = ""
                value_fields = ""

                if len([*data]) > 1:
                    fields = ", ".join(data.keys())
                    for i, key in enumerate(data.keys()):
                        value_fields += f"%({key})s, " if i != len(data.keys()
                                                                   ) - 1 else f"%({key})s"
                else:
                    fields = next(iter(data.keys()))

                sql = "INSERT INTO `" + table + \
                    "` (" + fields + ") VALUES (" + value_fields + ")"

                try:
                    print(f"Inserting data into {table}: ", end='')
                    cursor.execute(sql, data)
                    print("inserted with success!")
                    conn.commit()
                except mysql.connector.Error as err:
                    print(err)
                    return err

            cursor.close()
            conn.close()
            response = {
                "message": "Data inserted with success!",
                "data": data
            }

            return json.dumps(response, indent=4)

    # Query Data
    async def query_data(self, server, user, password, database, table, fields=None, condition=None):
        query = f"SELECT {fields} FROM {table}" if fields else f"SELECT * FROM {table}"
        if condition:
            query += f" WHERE {condition}"

        try:
            conn = mysql.connector.connect(
                host=server, user=user, passwd=password, db=database)
            cursor = conn.cursor()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
                return "Something is wrong with your user name or password"
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                return "Database does not exist"
            else:
                print(err)
                return err

        cursor.execute(query)
        row_headers = [x[0] for x in cursor.description]
        json_data = []
        for result in cursor.fetchall():
            json_data.append(dict(zip(row_headers, result)))
        result = cursor
        cursor.close()
        conn.close()
        return json.dumps(json_data, indent=4)


if __name__ == "__main__":
    asyncio.run(MySQL.run(), debug=True)
