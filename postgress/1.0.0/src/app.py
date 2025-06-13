import psycopg2
from psycopg2.extras import RealDictCursor
#from walkoff_app_sdk.app_base import AppBase
from shuffle_sdk import AppBase


class PostgreSQL(AppBase):
    __version__ = "1.0.0"
    app_name = "PostgreSQL"

    def __init__(self, redis, logger, console_logger=None):
        super().__init__(redis, logger, console_logger)

    def connect(self, host, port, dbname, user, password):
        conn = psycopg2.connect(
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
            with conn.cursor() as cur:
                cur.execute(query)
                try:
                    return {"result": cur.fetchall()}
                except psycopg2.ProgrammingError:
                    return {"message": "Query executed successfully, no data returned."}

if __name__ == "__main__":
    PostgreSQL.run()
