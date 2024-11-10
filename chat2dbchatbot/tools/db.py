import os
import psycopg2
#import streamlit as st

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

class DatabaseManager:
    def __init__(self, db_type='db'):
        self.db_type = db_type
        self.config = self._get_config()
    
    def _get_config(self):
        """Initialize database configuration"""
        is_dev = os.getenv('ENV') == 'dev'
        if self.db_type == 'db':
            db_params = {
                "dbname": os.getenv('DB_NAME', 'chatdb'),
                "user": os.getenv('DB_USER', 'postgres'),
                "password": os.getenv('DB_PASSWORD', 'postgres'),
                "host": os.getenv('DB_HOST', 'localhost' if is_dev else 'postgres'),
                "port": os.getenv('DB_PORT', '7433' if is_dev else '5432')
            }
        elif self.db_type == 'vecdb':
            db_params = {
                "dbname": os.getenv('VECDB_NAME', 'vecdb'),
                "user": os.getenv('VECDB_USER', 'postgres'),
                "password": os.getenv('VECDB_PASSWORD', 'postgres'),
                "host": os.getenv('VECDB_HOST', 'localhost' if is_dev else 'vecdb'),
                "port": os.getenv('VECDB_PORT', '6433' if is_dev else '5432')
            }
        else:
            raise ValueError("Invalid db_type. Expected 'db' or 'vecdb'.")
        return db_params
    
    def test_connection(self):
        """Test if database connection can be established."""
        try:
            conn = psycopg2.connect(**self.config)
            conn.close()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def get_table_names(self):
        """Get list of tables in the public schema."""
        conn = None
        try:
            conn = psycopg2.connect(**self.config)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [table[0] for table in cursor.fetchall()]
            return tables
        except Exception as e:
            print(f"Error fetching tables: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def execute_query_old(self, query, params=None):
        """Execute a query and return results."""
        conn = None
        try:
            conn = psycopg2.connect(**self.config)
            cursor = conn.cursor()
            cursor.execute(query, params)
            if query.lower().startswith('select'):
                results = cursor.fetchall()
                conn.close()
                return results
            else:
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"Query error: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: tuple = None) -> list:
        """Execute a SQL query and return the results.
        
        Args:
            query: SQL query string
            params: Optional tuple of query parameters
            
        Returns:
            List of query results or None if error
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.config)
            with conn.cursor() as cur:
                cur.execute(query, params)
                if cur.description:  # Check if query returns results
                    return cur.fetchall()
                conn.commit()
                return []
        except Exception as e:
            print(f"Database error: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def get_connection_string(self):
        """Generate a connection string in the format 'postgresql://username:password@host:port/dbname'"""
        return (
            f"postgresql://{self.config['user']}:{self.config['password']}@"
            f"{self.config['host']}:{self.config['port']}/{self.config['dbname']}"
        )