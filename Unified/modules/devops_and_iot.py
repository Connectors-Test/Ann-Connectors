import requests
import psycopg2
import redis
from elasticsearch import Elasticsearch
import time
from influxdb_client import InfluxDBClient

def fetch_from_clickhouse(creds, query):
    """
    creds: { 'base_url': str, 'user': str, 'password': str, 'database': str (optional) }
    query: SQL string to execute on ClickHouse
    """
    validation = validate_sql_query(query, engine="ClickHouse")
    if not validation["valid"]:
        return {"status": "error", "message": validation["error"]}
    query = validation["query"]
    try:
        # Ensure FORMAT JSON for structured output
        if not query.strip().lower().endswith("format json"):
            query = f"{query.strip()} FORMAT JSON"

        params = {}
        if 'database' in creds:
            params['database'] = creds['database']

        resp = requests.post(
            creds['base_url'], 
            params=params,
            data=query.encode("utf-8"),  # Explicit encoding for safety
            auth=(creds['user'], creds['password']),
            headers={"Content-Type": "text/plain"}  # ClickHouse expects raw SQL
        )
        resp.raise_for_status()
        return resp.json()

    except Exception as e:
        return {"status": "error", "message": f"ClickHouse fetch failed: {str(e)}"}

def fetch_from_tempo(creds, query, endpoint="search"):
    """
    creds: { 'base_url': str, 'username': str, 'api_token': str }
    query: dict for search query (serviceName, tags, etc.)
    endpoint: "search" for trace search, or "traces/{traceID}" for a specific trace
    """
    if not isinstance(query, dict):
        return {"status": "error", "message": "Tempo: query must be a dict"}

    if endpoint != "search" and not endpoint.startswith("traces/"):
        return {"status": "error", "message": "Tempo: invalid endpoint"}
    
    try:
        url = f"{creds['base_url']}/api/{endpoint}"
        resp = requests.get(url, params=query, auth=(creds['username'], creds['api_token']))
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": f"Tempo fetch failed: {str(e)}"}


def fetch_from_loki(creds, query, minutes):
    """
    creds: { 'base_url': str, 'username': str, 'api_token': str }
    query: LogQL query string
    minutes: number of minutes to look back for logs
    """
    if not query or not isinstance(query, str):
        return {"status": "error", "message": "Loki: query must be a string"}

    if minutes > 1440:  # max 24h lookback
        return {"status": "error", "message": "Loki: time range too large"}
    
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

def fetch_from_prometheus(creds, query):
    """
    creds: { 'base_url': str, 'username': str, 'api_token': str }
    query: PromQL query string
    """
    if not query or not isinstance(query, str):
        return {"status": "error", "message": "Prometheus: query must be a string"}
    try:
        url = f"{creds['base_url']}/api/prom/api/v1/query"
        resp = requests.get(url, params={"query": query}, auth=(creds['username'], creds['api_token']))
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": f"Prometheus fetch failed: {str(e)}"}
    
def fetch_from_influxdb(creds, flux_query):
    """
    creds: { 'url': str, 'token': str, 'bucket': str, 'org': str }
    flux_query: Flux language query
    """
    if not flux_query or not isinstance(flux_query, str):
        return {"status": "error", "message": "InfluxDB: query must be a string"}

    forbidden = ["drop", "delete"]
    if any(word in flux_query.lower() for word in forbidden):
        return {"status": "error", "message": "InfluxDB: forbidden keyword detected"}
    
    try:
        client = InfluxDBClient(url=creds["url"], token=creds["token"], org=creds["org"])
        query_api = client.query_api()
        result = query_api.query(org=creds["org"], query=flux_query)
        
        # Convert results to list of dicts (like SQL)
        data = [record.values for table in result for record in table.records]
        return data

    except Exception as e:
        return {"status": "error", "message": f"InfluxDB fetch failed: {str(e)}"}

def fetch_from_timescaledb(creds, query):
    """
    creds: { 'host': str, 'port': int, 'user': str, 'password': str, 'database': str }
    query: SQL query string
    """
    if query != "LIST_TABLES":
        validation = validate_sql_query(query, engine="TimescaleDB")
        if not validation["valid"]:
            return {"status": "error", "message": validation["error"]}
        query = validation["query"]
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

def fetch_from_redis(creds, command, args_str=""):
    """
    creds: { 'host': str, 'port': int, 'username': str (optional), 'password': str (optional) }
    command: Redis command name (string)
    args_str: comma-separated string of command arguments
    """
    allowed_commands = {"get", "mget", "hget", "hgetall", "lrange", "scan"}
    if command.lower() not in allowed_commands:
        return {"status": "error", "message": f"Redis: command '{command}' not allowed"}

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
    
def fetch_from_elasticsearch(creds, dsl_query, index):
    """
    creds: { 'cloud_id': str, 'user': str, 'password': str }
    index: Elasticsearch index name
    dsl_query: dict representing Elasticsearch query DSL
    """
    if not isinstance(dsl_query, dict):
        return {"status": "error", "message": "Elasticsearch: query must be a dict"}

    if not isinstance(index, str) or not index.strip():
        return {"status": "error", "message": "Elasticsearch: invalid index"}

    forbidden = ["delete", "update", "reindex"]
    if any(word in str(dsl_query).lower() for word in forbidden):
        return {"status": "error", "message": "Elasticsearch: forbidden operation detected"}

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