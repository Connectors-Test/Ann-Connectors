from dotenv import load_dotenv
import os
import sqlite3
from modules import *

load_dotenv()

CREDENTIALS = {
    "databricks": {
        "server_hostname": os.getenv("DATABRICKS_HOST_NAME"),
        "token": os.getenv("DATABRICKS_TOKEN"),
        "warehouse_id": os.getenv("DATABRICKS_WAREHOUSE_ID")
    },
    "postgresql": {
        "host": os.getenv("PG_HOST"),
        "port": int(os.getenv("PG_PORT")),
        "user": os.getenv("PG_USER"),
        "password": os.getenv("PG_PASSWORD"),
        "database": os.getenv("PG_DATABASE")
    },
    "supabase": {
        "uri": os.getenv("SUPABASE_URI"),
        "schema": os.getenv("SUPABASE_SCHEMA"),
        "table": os.getenv("SUPABASE_TABLE")
    },
    "mysql": {
        "host": os.getenv("MYSQL_HOST"),
        "port": int(os.getenv("MYSQL_PORT")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE")
    },
    "mongodb": {
        "uri": os.getenv("MONGO_URI"),
        "database": os.getenv("MONGO_DATABASE"),
        "collection": os.getenv("MONGO_COLLECTION")
    },
    "snowflake": {
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
        "table": os.getenv("SNOWFLAKE_TABLE")
    },
    "airtable": {
        "base_id": os.getenv("AIRTABLE_BASE_ID"),
        "api_key": os.getenv("AIRTABLE_API_KEY")
    },
    "neo4j": {
        "uri": os.getenv("NEO4J_URI"),
        "username": os.getenv("NEO4J_USERNAME"),
        "password": os.getenv("NEO4J_PASSWORD"),
        "database": os.getenv("NEO4J_DATABASE")
    }
}

# Metadata for LLM training
PRODUCT_METADATA = {
    "databricks": {
        "description": "Databricks SQL API for executing SQL queries.",
        "required_credentials": ["server_hostname", "token", "warehouse_id"],
        "required_parameters": ["credentials", "query"],
        "query_type": "SQL",
        "example_query": "SELECT * FROM sales LIMIT 10",
        "endpoint": "/api/2.0/sql/statements",
        "method": "POST",
        "headers": {"Authorization": "Bearer <TOKEN>"}
    },
    "postgresql": {
        "description": "PostgreSQL database connection using psycopg2.",
        "required_credentials": ["host", "port", "user", "password", "database"],
        "required_parameters": ["credentials", "query"],
        "query_type": "SQL",
        "example_query": "SELECT id, name FROM customers LIMIT 10"
    },
    "supabase": {
        "description": "Supabase database connection using psycopg2. Supabase is a hosted Postgres service that requires SSL connections.",
        "required_credentials": ["uri", "table", "schema"],  # or ["host", "port", "user", "password", "database"] if not using URI
        "required_parameters": ["credentials", "query"],
        "query_type": "SQL",
        "default_schema": "public",
        "notes": "When using URI, format should be: postgresql://<user>:<password>@<host>:<port>/<database>. SSL mode must be set to 'require'.",
        "example_query": "SELECT id, name FROM public.customers LIMIT 10"
    },
    "mysql": {
        "description": "MySQL database connection using mysql.connector.",
        "required_credentials": ["host", "port", "user", "password", "database"],
        "required_parameters": ["credentials", "query"],
        "query_type": "SQL",
        "example_query": "SELECT * FROM orders LIMIT 10"
    },
    "mongodb": {
        "description": "MongoDB connection using PyMongo.",
        "required_credentials": ["uri", "database", "collection"],
        "required_parameters": ["credentials", "query", "filter"],
        "query_type": "MongoDB Query/Filter",
        "example_query": '{"age": {"$gt": 30}}'
    },
    "snowflake": {
        "description": "Snowflake data warehouse connection.",
        "required_credentials": ["user", "password", "account", "warehouse", "database", "schema", "table"],
        "required_parameters": ["credentials", "query"],
        "query_type": "SQL",
        "example_query": "SELECT * FROM products LIMIT 10"
    },
    "airtable": {
        "description": "Airtable API for accessing tables.",
        "required_credentials": ["base_id", "api_key"],
        "required_parameters": ["credentials", "table_name", "filterByFormula"],
        "query_type": "Formula Expression",
        "example_query": "FIND('Laptop', {ProductName})"
    },
    "neo4j": {
        "description": "Neo4j graph database connection using the official Python driver.",
        "required_credentials": ["uri", "username", "password", "database"],
        "required_parameters": ["credentials", "query"],
        "query_type": "Cypher",
        "example_query": "MATCH (n:DevOps) RETURN n LIMIT 10"
    }
}

DB_NAME = "wwwsmart_credentials.db"
conn = sqlite3.connect(DB_NAME)
conn.close()

create_table(DB_NAME, "Api_connector_credentials")
create_table(DB_NAME, "Db_connector_credentials")

import uuid

dummy_userid = str(uuid.uuid4())
dummy_uuid = "user_001"
dummy_username = "testuser"

for product, creds in CREDENTIALS.items():
    required_keys = PRODUCT_METADATA[product]["required_credentials"]
    filtered_creds = {k: v for k, v in creds.items() if k in required_keys}
    
    try:
        upsert_credential(
            db_name=DB_NAME,
            table="Db_connector_credentials",
            userid=dummy_userid,
            uuid=dummy_uuid,
            username=dummy_username,
            name=product,
            credentials=filtered_creds,
            metadata=json.dumps(PRODUCT_METADATA[product])
        )
        print(f"✅ Inserted {product}")
    except ValueError as ve:
        print(f"❌ Skipped {product}: {ve}")
