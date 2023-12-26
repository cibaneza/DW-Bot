import snowflake.connector
from google.cloud import bigquery
import pandas as pd
from app_secrets import *

client_bq = bigquery.Client()
project_id = "xepelin-ds-prod"


def run_query(query):
    query_job = client_bq.query(query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.cache_data to hash the return value.
    rows = [dict(row) for row in rows_raw]
    return rows


def execute_bq_query(sql):
    try:
        # Execute the query
        query_job = client_bq.query(sql)
        rows_raw = query_job.result()

        # Convert to list of dicts
        print(sql)
        print(query_job)
        rows = [dict(row) for row in rows_raw]

        # Create a DataFrame
        data_frame = pd.DataFrame(rows)
        return data_frame

    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an exception


def execute_sf_query(sql):
    # Snowflake connection parameters
    connection_params = {
        "user": SF_USER,
        "password": SF_PASSWORD,
        "account": SF_ACCOUNT,
        "warehouse": SF_WAREHOUSE,
        "database": SF_DATABASE,
        "schema": SF_SCHEMA,
        "role": SF_ROLE,
    }

    query = sql

    try:
        # Establish a connection to Snowflake
        conn = snowflake.connector.connect(**connection_params)

        # Create a cursor object
        cur = conn.cursor()

        # Execute the query
        try:
            cur.execute(query)
        except snowflake.connector.errors.ProgrammingError as pe:
            print("Query Compilation Error:", pe)
            return "Query compilation error"

        # Fetch all results
        query_results = cur.fetchall()

        # Get column names from the cursor description
        column_names = [col[0] for col in cur.description]

        # Create a Pandas DataFrame
        data_frame = pd.DataFrame(query_results, columns=column_names)

        # Print the DataFrame
        # print(data_frame)
        return data_frame

    except snowflake.connector.errors.DatabaseError as de:
        print("Snowflake Database Error:", de)

    except Exception as e:
        print("An error occurred:", e)

    finally:
        # Close the cursor and connection
        try:
            cur.close()
        except:
            pass

        try:
            conn.close()
        except:
            pass


if __name__ == "__main__":
    # Snowflake query
    query = """
            SELECT * FROM `xepelin-ds-prod.prod_int.MasterOrderInvoice` 
    """
    execute_bq_query(query)
