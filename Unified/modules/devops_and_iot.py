import requests
import psycopg2
import redis
from elasticsearch import Elasticsearch
import time
from influxdb_client import InfluxDBClient

# ------------------------
# ClickHouse - SQL over HTTP/Native
# ------------------------
def fetch_from_clickhouse(creds, query):
    """
    creds: { 'base_url': str, 'user': str, 'password': str, 'database': str (optional) }
    query: SQL string to execute on ClickHouse
    """
    try:
        # Ensure FORMAT JSON for structured output
        if not query.strip().lower().endswith("format json"):
            query = f"{query.strip()} FORMAT JSON"

        params = {}
        if 'database' in creds:
            params['database'] = creds['database']

        resp = requests.post(
            creds['base_url'],  # Should already have https://...:8443
            params=params,
            data=query.encode("utf-8"),  # Explicit encoding for safety
            auth=(creds['user'], creds['password']),
            headers={"Content-Type": "text/plain"}  # ClickHouse expects raw SQL
        )
        resp.raise_for_status()
        return resp.json()

    except Exception as e:
        return {"status": "error", "message": f"ClickHouse fetch failed: {str(e)}"}

# ------------------------
# Tempo - JSON GET to /api/search or /api/traces
# ------------------------
def fetch_from_tempo(creds, query, endpoint="search"):
    """
    creds: { 'base_url': str, 'username': str, 'api_token': str }
    query: dict for search query (serviceName, tags, etc.)
    endpoint: "search" for trace search, or "traces/{traceID}" for a specific trace
    """
    try:
        url = f"{creds['base_url']}/api/{endpoint}"
        resp = requests.get(url, params=query, auth=(creds['username'], creds['api_token']))
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": f"Tempo fetch failed: {str(e)}"}


# ------------------------
# Loki - GET /loki/api/v1/query or /query_range
# ------------------------
def fetch_from_loki(creds, query, minutes):
    try:
        url = f"{creds['base_url']}/loki/api/v1/query_range"
        end = int(time.time() * 1e9)  # nanoseconds
        start = end - (minutes * 60 * int(1e9))
        params = {
            "query": query,
            "limit": 100,
            "start": start,
            "end": end,
            "direction": "backward"
        }
        resp = requests.get(url, params=params,
                            auth=(creds['username'], creds['api_token']))
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": f"Loki fetch failed: {str(e)}"}

# ------------------------
# Prometheus - GET /api/v1/query
# ------------------------
def fetch_from_prometheus(creds, query):
    """
    creds: { 'base_url': str, 'username': str, 'api_token': str }
    query: PromQL query string
    """
    try:
        url = f"{creds['base_url']}/api/prom/api/v1/query"
        resp = requests.get(url, params={"query": query}, auth=(creds['username'], creds['api_token']))
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": f"Prometheus fetch failed: {str(e)}"}
    
# ------------------------
# InfluxDB - POST Flux query to /api/v2/query
# ------------------------
def fetch_from_influxdb(creds, flux_query):
    """
    creds: { 'url': str, 'token': str, 'bucket': str, 'org': str }
    flux_query: Flux language query
    """
    try:
        client = InfluxDBClient(url=creds["url"], token=creds["token"], org=creds["org"])
        query_api = client.query_api()
        result = query_api.query(org=creds["org"], query=flux_query)
        
        # Convert results to list of dicts (like SQL)
        data = [record.values for table in result for record in table.records]
        return data

    except Exception as e:
        return {"status": "error", "message": f"InfluxDB fetch failed: {str(e)}"}

# ------------------------
# TimescaleDB - PostgreSQL SQL execution
# ------------------------
def fetch_from_timescaledb(creds, query):
    """
    creds: { 'host': str, 'port': int, 'user': str, 'password': str, 'database': str }
    query: SQL query string
    """
    if query == "LIST_TABLES":
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
    conn = None
    try:
        conn = psycopg2.connect(
            host=creds['host'],
            port=creds['port'],
            user=creds['user'],
            password=creds['password'],
            database=creds['database']
        )
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        return {"status": "error", "message": f"TimescaleDB fetch failed: {str(e)}"}
    finally:
        if conn:
            conn.close()

# ------------------------
# Redis - direct command execution
# ------------------------
def fetch_from_redis(creds, command, args_str=""):
    """
    creds: { 'host': str, 'port': int, 'username': str (optional), 'password': str (optional) }
    command: Redis command name (string)
    args_str: comma-separated string of command arguments
    """
    try:
        r = redis.Redis(
            host=creds['host'],
            port=creds['port'],
            username=creds.get('username'),
            password=creds.get('password'),
            decode_responses=True
        )
        func = getattr(r, command.lower(), None)
        if not func:
            raise ValueError(f"Unsupported Redis command: {command}")

        # Split comma-separated args and strip spaces
        args = [arg.strip() for arg in args_str.split(",")] if args_str else []

        return func(*args)
    except Exception as e:
        return {"status": "error", "message": f"Redis fetch failed: {str(e)}"}
    
# ------------------------
# Elasticsearch - POST DSL to /{index}/_search
# ------------------------
def fetch_from_elasticsearch(creds, dsl_query, index):
    """
    creds: { 'cloud_id': str, 'user': str, 'password': str }
    index: Elasticsearch index name
    dsl_query: dict representing Elasticsearch query DSL
    """
    try:
        es = Elasticsearch(
            cloud_id=creds["cloud_id"],
            basic_auth=(creds["username"], creds["password"])
        )

        resp = es.search(index=index, body=dsl_query)
        return resp

    except Exception as e:
        return {
            "status": "error",
            "message": f"Elasticsearch fetch failed: {str(e)}"
        }
