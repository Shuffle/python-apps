from psycopg2 import connect, ProgrammingError
from psycopg2.extras import RealDictCursor
from shuffle_sdk import AppBase


class PostgreSQL(AppBase):
    __version__ = "1.1.0"
    app_name = "PostgreSQL"

    def __init__(self, redis, logger, console_logger=None):
        super().__init__(redis, logger, console_logger)

    @staticmethod
    def connect(host, port, dbname, user, password):
        conn = connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            cursor_factory=RealDictCursor
        )
        return conn

    def run_query(self, host, port, dbname, user, password, query):
        with self.connect(host, port, dbname, user, password) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                try:
                    return {"result": [dict(row) for row in cur.fetchall() if row]}
                except ProgrammingError:
                    return {"message": "Query executed successfully, no data returned."}


if __name__ == "__main__":
    PostgreSQL.run()
