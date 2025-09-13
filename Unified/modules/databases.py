import json
import requests
from flask import jsonify
import databricks.sql
import psycopg2
import psycopg2.extras
from pymongo import MongoClient
from bson import json_util, ObjectId
import mysql.connector
from neo4j import GraphDatabase
from neo4j.time import DateTime
from config import DB_CONFIG

def fetch_from_databricks(creds, query=None):
    conn = None
    cursor = None
    
    validation = validate_sql_query(query, engine="PostgreSQL")
    if not validation["valid"]:
        return {"status": "error", "message": validation["error"]}
    query = validation["query"]

    try:
        # Connect
        conn = databricks.sql.connect(
            server_hostname=creds["server_hostname"],
            http_path=creds["warehouse_id"],
            access_token=creds["token"]
        )
        cursor = conn.cursor()

        cursor.execute(query)

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

def fetch_from_postgresql(creds, query=None):
    conn = None
    cur = None
    
    validation = validate_sql_query(query, engine="postgresql")
    if not validation["valid"]:
        return {"status": "error", "message": validation["error"]}
    query = validation["query"]

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

        # Execute
        cur.execute(query)
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

def fetch_from_supabase(creds, query=None):
    """
    Fetch data from Supabase using either a query or table reference.
    Args:
        creds (dict): Must have 'uri' for Supabase connection.
        query (str, optional): SQL query string.
    Returns:
        list[dict]: Query results as list of dicts.
    """
    conn = None
    cur = None
    
    validation = validate_sql_query(query, engine="PostgreSQL")
    if not validation["valid"]:
        return {"status": "error", "message": validation["error"]}
    query = validation["query"]

    try:
        conn = psycopg2.connect(creds["uri"], sslmode="require")
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute(query)
        rows = cur.fetchall()
        return [dict(row) for row in rows]

    except Exception as e:
        return {"status": "error", "message": f"Supabase fetch failed: {str(e)}"}
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def fetch_from_mysql(creds, query=None):
    """
    Fetch data from MySQL using a query or collection reference.
    Args:
        creds (dict): Must have 'host', 'port', 'user', 'password', 'database'.
        query (str, optional): SQL query string.
    Returns:
        list[dict]: Query results as list of dicts.
    """
    conn = None
    cur = None
    
    validation = validate_sql_query(query, engine="MySQL")
    if not validation["valid"]:
        return {"status": "error", "message": validation["error"]}
    query = validation["query"]

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

        # Execute
        cur.execute(query)
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

def serialize_document(doc):                                      # For formatting MongoDB results to JSON-friendly types
    if isinstance(doc, list):
        return [serialize_document(d) for d in doc]
    if isinstance(doc, dict):
        return {k: serialize_document(v) for k, v in doc.items()}
    if isinstance(doc, ObjectId):
        return str(doc)
    return doc

def fetch_from_mongodb(creds, query=None, collection=None, database=None, limit=None):
    """
    Fetch data from MongoDB using a query or collection reference.
    Args:
        creds (dict): Must have 'uri' for MongoDB connection.
        query (str or dict, optional): MongoDB query as JSON string or dict.
        collection (str, optional): Collection name to fetch data from.
        database (str, optional): Database name if not provided in creds.
    Returns:
        list[dict]: Query results as list of dicts.
    """
    creds = DB_CONFIG["mongodb"]
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
                    raise ValueError("MongoDB query must be a JSON string or dict")
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

def fetch_from_snowflake(creds, query=None, database=None, schema=None):
    """
    Fetch data from Snowflake using either a query or table reference.
    Args:
        creds (dict): Must have 'user', 'password', 'account', 'warehouse', 'database', 'schema'.
        query (str, optional): SQL query string.
        database (str, optional): Database name if not provided in creds.
        schema (str, optional): Schema name if not provided in creds.
    Returns:
        list[dict]: Query results as list of dicts.
    """
    conn = None
    cur = None
    
    validation = validate_sql_query(query, engine="PostgreSQL")
    if not validation["valid"]:
        return {"status": "error", "message": validation["error"]}
    query = validation["query"]
    
    try:
        # Resolve table/schema/database
        database = database or creds.get("database")
        schema = schema or creds.get("schema")
        table = creds.get("table")

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
                if not isinstance(query_params_raw, str):
                    return {"valid": False, "error": "Airtable params must be JSON or formula string"}

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

def serialize_value(value):                                               # Convert Neo4j values to JSON-friendly types
    # Convert Neo4j special types to JSON-friendly ones
    if isinstance(value, DateTime):
        return value.iso_format()  # or str(value) if you want a simple string
    if hasattr(value, "items"):  # Node or Relationship
        return {k: serialize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialize_value(v) for v in value]
    return value

def fetch_from_neo4j(creds, query=None):
    """
    Fetch data from a Neo4j database.

    Args:
        creds (dict): Must have 'uri', 'username', 'password', 'database'.
        query (str, optional): Cypher query string. 

    Returns:
        list[dict]: Query results as list of dicts.
    """
    creds = DB_CONFIG["neo4j"]
    driver = None
    if not query or not query.strip():
        return {"error": "Neo4j: Query must be provided"}
    
    lowered = query.strip().lower()
    
    if not (lowered.startswith("match") or lowered.startswith("call")):
        return {"error": "Neo4j: Only MATCH or CALL queries are allowed"}
    
    forbidden = ["create", "delete", "merge", "set", "drop"]
    if any(f" {word} " in lowered for word in forbidden):
        return {"error": f"Neo4j: Forbidden keyword detected"}
    
    try:
        # Connect to Neo4j
        driver = GraphDatabase.driver(
            creds["uri"],
            auth=(creds["username"], creds["password"])
        )

        # Run query
        with driver.session(database=creds.get("database", "neo4j")) as session:
            results = session.run(query)
            data = []
            for record in results:
                clean_record = {}
                for key, value in record.items():
                    clean_record[key] = serialize_value(value)
                data.append(clean_record)
            # return data
            return {"status": "success", "data": data}

    except Exception as e:
        return {
            "status": "error",
            "message": f"Neo4j fetch failed: {str(e)}"
        }
    finally:
        if driver:
            driver.close()
    
def validate_sql_query(query: str, engine: str = "generic"):
    """
    Validate a SQL query to ensure safety (read-only, correct format).
    
    Args:
        query (str): The SQL query string
        engine (str): Name of the engine (used for error messages/logging)
    
    Returns:
        dict: {"valid": True, "query": query} or {"valid": False, "error": "..."}
    """
    if not query or not query.strip():
        return {"valid": False, "error": f"{engine}: Query must be provided"}
    
    lowered = query.strip().lower()

    # must start with SELECT
    if not lowered.startswith("select"):
        return {"valid": False, "error": f"{engine}: Only SELECT queries are allowed"}
    
    # block forbidden keywords
    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate", "create", "grant", "revoke"]
    if any(f" {word} " in lowered for word in forbidden):
        return {"valid": False, "error": f"{engine}: Forbidden keyword detected"}
    
    # must contain FROM
    if " from " not in lowered:
        return {"valid": False, "error": f"{engine}: Invalid query (missing FROM clause)"}

    return {"valid": True, "query": query}