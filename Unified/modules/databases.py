import json
import requests
from flask import jsonify
import databricks.sql
import psycopg2
import psycopg2.extras
from pymongo import MongoClient
from bson import json_util, ObjectId
import mysql.connector

def fetch_from_databricks(creds, query=None, table=None, database=None):
    conn = None
    cursor = None
    try:
        # Connect
        conn = databricks.sql.connect(
            server_hostname=creds["server_hostname"],
            http_path=creds["warehouse_id"],
            access_token=creds["token"]
        )
        cursor = conn.cursor()

        # Decide query
        if query:
            # Normalize spaces
            query_clean = " ".join(query.strip().split())
            query_lower = query_clean.lower()

            # If FROM is missing, inject it before LIMIT (if present) from query arguments
            if "from" not in query_lower:
                if not (database and table):
                    raise ValueError("Query missing FROM clause and database/table not provided")
                
                if "limit" in query_lower:
                    limit_index = query_lower.index("limit")
                    before_limit = query_clean[:limit_index].strip()
                    after_limit = query_clean[limit_index:].strip()
                    query_clean = f"{before_limit} FROM {database}.{table} {after_limit}"
                    
                else:
                    query_clean = f"{query_clean} FROM {database}.{table}"
            sql_query = query_clean

        elif database and table:
            sql_query = f"SELECT * FROM {database}.{table}"
        else:
            raise ValueError("Either query or both database and table must be provided")

        cursor.execute(sql_query)

        # Extract results
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]

        return results

    except Exception as e:
        return {
            "status": "error",
            "message": f"Databricks fetch failed: {str(e)}"
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def fetch_from_postgresql(creds, query=None, table=None, schema=None):
    conn = None
    cur = None
    try:
        # Connect
        conn = psycopg2.connect(
            host=creds["host"],
            port=creds["port"],
            user=creds["user"],
            password=creds["password"],
            database=creds["database"]
        )

        # Use DictCursor so fetch results are dicts directly
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Decide query
        if query:
            sql_query = query.strip()

            # If query has no FROM and table is provided, add FROM before LIMIT
            if " from " not in sql_query.lower() and table:
                table_ref = f'"{schema}"."{table}"' if schema else f'"{table}"'

                # Case 1: Query already has LIMIT — we must insert FROM before it
                limit_index = sql_query.lower().find(" limit ")
                if limit_index != -1:
                    select_part = sql_query[:limit_index].strip()  # before LIMIT
                    limit_part = sql_query[limit_index:].strip()   # the LIMIT itself
                    sql_query = f"{select_part} FROM {table_ref} {limit_part}"
                else:
                    sql_query = f"{sql_query} FROM {table_ref}"

        elif table:
            table_ref = f'"{schema}"."{table}"' if schema else f'"{table}"'
            sql_query = f'SELECT * FROM {table_ref}'
        else:
            raise ValueError("Either query or both database and table must be provided")

        # Execute
        cur.execute(sql_query)
        rows = cur.fetchall()

        # Convert to list of dicts
        results = [dict(row) for row in rows]

        return results

    except Exception as e:
        return {
            "status": "error",
            "message": f"PostgreSQL fetch failed: {str(e)}"
        }
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def fetch_from_mysql(creds, query=None, table=None, schema=None):
    conn = None
    cur = None
    try:
        # Connect
        conn = mysql.connector.connect(
            host=creds["host"],
            port=creds["port"],
            user=creds["user"],
            password=creds["password"],
            database=creds["database"]
        )
        cur = conn.cursor(dictionary=True)  # dictionary=True => dict rows

        if table:
            table = table.strip()

        # Decide query
        if query:
            sql_query = query.strip()

            if " from " not in sql_query.lower() and table:
                table_ref = f"`{schema}`.`{table}`" if schema else f"`{table}`"

                limit_index = sql_query.lower().find(" limit ")
                if limit_index != -1:
                    select_part = sql_query[:limit_index].strip()
                    limit_part = sql_query[limit_index:].strip()
                    sql_query = f"{select_part} FROM {table_ref} {limit_part}"
                else:
                    sql_query = f"{sql_query} FROM {table_ref}"
        elif table:
            table_ref = f"`{schema}`.`{table}`" if schema else f"`{table}`"
            sql_query = f"SELECT * FROM {table_ref}"
        else:
            raise ValueError("Either query or table must be provided")

        # Execute
        cur.execute(sql_query)
        rows = cur.fetchall()

        return rows  # already dicts

    except Exception as e:
        return {
            "status": "error",
            "message": f"MySQL fetch failed: {str(e)}"
        }
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def serialize_document(doc): ## For formatting MongoDB results
    if isinstance(doc, list):
        return [serialize_document(d) for d in doc]
    if isinstance(doc, dict):
        return {k: serialize_document(v) for k, v in doc.items()}
    if isinstance(doc, ObjectId):
        return str(doc)
    return doc

def fetch_from_mongodb(creds, query=None, collection=None, database=None, limit=None):
    client = None
    try:
        # Connect
        client = MongoClient(creds["uri"])
        db = client[database or creds.get("database")]
        collection = collection or creds.get("collection")
        if not collection:
            raise ValueError("Collection name must be provided for MongoDB queries")

        coll = db[collection]

        # Decide query
        if query:
            try:
                # Try parsing query if passed as JSON string
                if isinstance(query, str):
                    query_dict = json_util.loads(query)
                elif isinstance(query, dict):
                    query_dict = query
                else:
                    raise ValueError("Query must be a JSON string or dict")
            except Exception as e:
                raise ValueError(f"Invalid MongoDB query: {e}")
        else:
            query_dict = {}

        cursor = coll.find(query_dict)

        if limit:
            cursor = cursor.limit(int(limit))

        # Convert cursor to list and serialize BSON to JSON-friendly types
        results = list(cursor)
        return serialize_document(results)

    except Exception as e:
        return {
            "status": "error",
            "message": f"MongoDB fetch failed: {str(e)}"
        }
    finally:
        if client:
            client.close()

import snowflake.connector

def fetch_from_snowflake(creds, query=None, table=None, database=None, schema=None):
    conn = None
    cur = None
    try:
        # Resolve table/schema/database
        database = database or creds.get("database")
        schema = schema or creds.get("schema")
        table = table or creds.get("table")

        # Connect
        conn = snowflake.connector.connect(
            user=creds["user"],
            password=creds["password"],
            account=creds["account"],
            warehouse=creds["warehouse"],
            database=database,
            schema=schema
        )
        cur = conn.cursor()

        # Build query
        if query:
            sql_query = query.strip()

            # Inject table if missing FROM
            if " from " not in sql_query.lower() and table:
                table_ref = f'"{database}"."{schema}"."{table}"' if schema and database else f'"{table}"'
                limit_index = sql_query.lower().find(" limit ")
                if limit_index != -1:
                    select_part = sql_query[:limit_index].strip()
                    limit_part = sql_query[limit_index:].strip()
                    sql_query = f"{select_part} FROM {table_ref} {limit_part}"
                else:
                    sql_query = f"{sql_query} FROM {table_ref}"
        elif table:
            table_ref = f'"{database}"."{schema}"."{table}"' if schema and database else f'"{table}"'
            sql_query = f"SELECT * FROM {table_ref}"
        else:
            raise ValueError("Either query or both database and table must be provided")

        # Execute
        cur.execute(sql_query)

        # Extract results
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        results = [dict(zip(columns, row)) for row in rows]

        return results

    except Exception as e:
        return {
            "status": "error",
            "message": f"Snowflake fetch failed: {str(e)}"
        }
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def fetch_from_airtable(creds, table_name, query_params_raw=None):
    """
    Fetch records from Airtable with optional filtering, sorting, and pagination.

    Args:
        creds (dict): Airtable credentials with keys 'base_id' and 'api_key'.
        table_name (str): Airtable table name.
        query_params_raw (str, optional): Raw query parameters (JSON or Airtable formula).

    Returns:
        tuple: (Flask Response, HTTP status code)
    """
    try:
        # Build API endpoint & headers
        url = f"https://api.airtable.com/v0/{creds['base_id']}/{table_name}"
        headers = {"Authorization": f"Bearer {creds['api_key']}"}

        # Parse incoming query params
        query_params = {}
        if query_params_raw:
            try:
                query_params = json.loads(query_params_raw)  # JSON-based query
            except json.JSONDecodeError:
                query_params = {"filterByFormula": query_params_raw}  # formula string

        all_records = []
        offset = None

        while True:
            # Flatten params for Airtable
            params = []
            for key, value in query_params.items():
                if isinstance(value, list):
                    for item in value:
                        params.append((key, item))
                else:
                    params.append((key, value))

            if offset:
                params.append(("offset", offset))

            # Make request
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            resp_json = response.json()

            if 'error' in resp_json:
                return jsonify({
                    "status": "error",
                    "message": resp_json["error"]["message"]
                }), 400

            # Add new batch of records
            records = resp_json.get("records", [])
            all_records.extend(records)

            # Handle pagination
            offset = resp_json.get("offset")
            if not offset:
                break

        # Format clean output (fields + id)
        formatted_data = []
        for record in all_records:
            fields = record.get("fields", {})
            fields["id"] = record.get("id")
            formatted_data.append(fields)

        return formatted_data, 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Airtable fetch failed: {str(e)}"
        }), 500