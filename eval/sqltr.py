import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

#For calling DB with expected and generated SQL to obtain result and convert to dataframe

class SQLTestRun:
    def __init__(self):
        self.is_dev = (os.getenv('ENV') == 'dev')
        self.db_config = {
            "host": os.getenv('DB_HOST', 'localhost' if self.is_dev else 'postgres'),
            "port": os.getenv('DB_PORT', '7433' if self.is_dev else '5432'),
            "dbname": os.getenv('DB_NAME', 'chatdb'),
            "user": os.getenv('DB_USER', 'postgres'),
            "password": os.getenv('DB_PASSWORD', 'postgres'),
        }

    def run_sql_result(self, query):
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            return self.fetch_query_results(query, conn)
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def fetch_query_results(self, query, connection):
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(result, columns=columns)