import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

is_dev = os.getenv('ENV') == 'dev'

# Database connection settings
db_config = {
    "host": os.getenv('DB_HOST', 'localhost' if is_dev else 'postgres'),
    "port": os.getenv('DB_PORT', '7433' if is_dev else '5432'),
    "dbname": os.getenv('DB_NAME', 'chatdb'),
    "user": os.getenv('DB_USER', 'postgres'),
    "password": os.getenv('DB_PASSWORD', 'postgres'),
}

# Function to execute a query and fetch the results
def fetch_query_results(query, connection):
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(result, columns=columns)

# Function to compare two dataframes
# def compare_query_results(df1, df2):
#     if df1.equals(df2):
#         # print("The results are identical.")
#         return "The results are identical."
#     else:
#         # print("The results differ!")
#         # # Find differences
#         # print("\nRows in Query 1 but not in Query 2:")
#         # print(df1[~df1.apply(tuple, axis=1).isin(df2.apply(tuple, axis=1))])
#         # print("\nRows in Query 2 but not in Query 1:")
#         # print(df2[~df2.apply(tuple, axis=1).isin(df1.apply(tuple, axis=1))])

def run_compare_query_results(query1, query2):
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_config)
        
        # Fetch results for each query
        results1 = fetch_query_results(query1, conn)
        results2 = fetch_query_results(query2, conn)

        print(results1.head(1))
        print(results2.head(1))
        
        # Compare the results
        isEqualRespon = results1.equals(results2)

        if 'conn' in locals() and conn:
            conn.close()

        return isEqualRespon

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    finally:
        if 'conn' in locals() and conn:
            conn.close()