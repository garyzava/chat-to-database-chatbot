# app.py
import streamlit as st
import psycopg2
from psycopg2 import sql

# Database connection parameters
db_params = {
    "dbname": "chatdb",
    "user": "postgres",
    "password": "postgres",
    "host": "postgres",
    "port": "5432",
}

# Connect to the database
def get_table_names():
    conn = None
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        tables = cursor.fetchall()
        cursor.close()
        return [table[0] for table in tables]
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        if conn:
            conn.close()

st.title("Database Table Names")
st.write("Tables in `chatdb`:")
tables = get_table_names()
if tables:
    st.write(tables)
else:
    st.write("No tables found or failed to connect to the database.")