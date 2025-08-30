import os
from dotenv import load_dotenv
from ..modules import *
import uuid

load_dotenv()

CREDENTIALS_DOI = {
    "clickhouse": {
        "base_url": os.getenv("CLICKHOUSE_URL"),
        "user": os.getenv("CLICKHOUSE_USER"),
        "password": os.getenv("CLICKHOUSE_PASSWORD"),
        "database": os.getenv("CLICKHOUSE_DATABASE", "default")
    },
    "tempo": {
        "base_url": os.getenv("TEMPO_BASE_URL"),
        "username": os.getenv("TEMPO_USERNAME"),
        "api_token": os.getenv("TEMPO_API_TOKEN")
    },
    "loki": {
        "base_url": os.getenv("LOKI_BASE_URL"),
        "username": os.getenv("LOKI_USERNAME"),
        "api_token": os.getenv("LOKI_API_TOKEN")
    },
    "prometheus": {
        "base_url": os.getenv("PROM_BASE_URL"),
        "username": os.getenv("PROM_USERNAME"),
        "api_token": os.getenv("PROM_API_TOKEN")
    },
    "influxdb": {
        "url": os.getenv("INFLUX_URL"),
        "token": os.getenv("INFLUX_TOKEN"),
        "org": os.getenv("INFLUX_ORG"),
        "bucket": os.getenv("INFLUX_BUCKET")
    },
    "timescaledb": {
        "host": os.getenv("TS_HOST"),
        "port": int(os.getenv("TS_PORT", "5432")),
        "user": os.getenv("TS_USER"),
        "password": os.getenv("TS_PASSWORD"),
        "database": os.getenv("TS_DATABASE"),
        "sslmode": os.getenv("TS_SSLMODE", "prefer")
    },
    "redis": {
        "host": os.getenv("REDIS_HOST"),
        "port": int(os.getenv("REDIS_PORT")),
        "username": os.getenv("REDIS_USER", "default"),
        "password": os.getenv("REDIS_PASS")
    },
    "elasticsearch": {
        "cloud_id": os.getenv("ES_CLOUD_ID"),
        "username": os.getenv("ES_USERNAME"),
        "password": os.getenv("ES_PASSWORD"),
        "default_index": os.getenv("ES_DEFAULT_INDEX", "logs-*")
    },
        "opensearch": {
        "host": os.getenv("OS_HOST", "http://localhost:9200"),
        "username": os.getenv("OS_USERNAME", "admin"),
        "password": os.getenv("OS_PASSWORD"),
        "default_index": os.getenv("OS_DEFAULT_INDEX", "logs-*")
    }
}

PRODUCT_METADATA_DOI = {
    "clickhouse": {
        "description": "ClickHouse columnar DB over HTTP/native; run SQL queries.",
        "required_credentials": ["base_url", "user", "password", "database"],
        "required_parameters": ["credentials", "query"],
        "query_type": "SQL",
        "example_query": "SELECT * FROM system.tables LIMIT 10",
        "notes": "Base URL should include protocol and port (e.g., https://host:8443/). POST query with 'FORMAT JSON' for structured results."
    },
    "tempo": {
        "description": "Grafana Tempo trace backend via HTTP API.",
        "required_credentials": ["base_url", "username", "api_token"],
        "required_parameters": ["credentials", "search_body"],
        "query_type": "Trace Query",
        "example_query": '{"serviceName":"checkout","start":"-5m","end":"now"}',
        "notes": "Use /api/search or /api/traces endpoints on the Grafana Cloud Tempo URL. Auth via Basic Auth or Bearer token from Grafana Service Account."
    },
    "loki": {
        "description": "Grafana Loki log backend via HTTP API (query_range used for recent logs).",
        "required_credentials": ["base_url", "username", "api_token"],
        "required_parameters": ["credentials", "logql", "minutes"],
        "query_type": "LogQL",
        "example_query": '{app="api"} |= "error" | line_format "{{.message}}"',
        "notes": "API path /loki/api/v1/query_range with start/end nanoseconds. Auth via Basic Auth using Grafana Service Account."
    },
    "prometheus": {
        "description": "Prometheus time-series via HTTP API.",
        "required_credentials": ["base_url", "username", "api_token"],
        "required_parameters": ["credentials", "promql"],
        "query_type": "PromQL",
        "example_query": 'rate(http_requests_total[5m])',
        "notes": "Base URL is Prometheus endpoint from Grafana Cloud (e.g., https://prometheus-<region>.grafana.net/api/prom). Auth via Bearer token or Basic Auth."
    },
    "influxdb": {
        "description": "InfluxDB 2.x using Flux queries.",
        "required_credentials": ["url", "token", "org", "bucket"],
        "required_parameters": ["credentials", "flux_query"],
        "query_type": "Flux",
        "example_query": 'from(bucket:"my-bucket") |> range(start:-1h) |> filter(fn:(r) => r._measurement == "cpu")',
        "notes": "Use official InfluxDBClient. Ensure bucket exists. Returns list of dicts with record values."
    },
    "timescaledb": {
        "description": "TimescaleDB (PostgreSQL) for time-series; run SQL queries.",
        "required_credentials": ["host", "port", "user", "password", "database", "sslmode"],
        "required_parameters": ["credentials", "query"],
        "query_type": "SQL",
        "example_query": "SELECT time_bucket('5 minutes', ts) AS bucket, avg(value) FROM metrics GROUP BY bucket ORDER BY bucket DESC LIMIT 12",
        "notes": "Optional: use DictCursor for easier JSON conversion."
    },
    "redis": {
        "description": "Redis key-value store; direct command execution.",
        "required_credentials": ["host", "port", "username", "password"],
        "required_parameters": ["credentials", "command", "args_str"],
        "query_type": "Redis Command",
        "example_query": 'LRANGE logs 0 10',
        "notes": "Split comma-separated args for commands. Ensure command name matches Redis Python client method (case-insensitive)."
    },
    "elasticsearch": {
        "description": "Elasticsearch via REST or official client; DSL queries supported.",
        "required_credentials": ["cloud_id", "username", "password"],
        "required_parameters": ["credentials", "index", "dsl_query"],
        "query_type": "Elasticsearch DSL",
        "example_query": '{"query":{"match":{"message":"error"}},"size":10}',
        "notes": "Use cloud_id and basic_auth. Returns full Elasticsearch response dict. Ensure index exists."
    },
    "opensearch": {
        "description": "OpenSearch via REST or official client; DSL queries supported.",
        "required_credentials": ["host", "username", "password"],
        "required_parameters": ["credentials", "index", "dsl_query"],
        "query_type": "OpenSearch DSL",
        "example_query": '{"query": {"match": {"message": "error"}}, "size": 10}',
        "notes": "Connect directly to OpenSearch endpoint. Use HTTP(S) host, not cloud_id. Ensure index exists."
    }
}

DB_NAME = "Unified/sqlite/wwwsmart_credentials.db"

# Create DoI table (DevOps & IoT)
create_table(DB_NAME, "DoI_connector_credentials")

dummy_userid = str(uuid.uuid4())
dummy_uuid = "user_001"
dummy_username = "testuser"

# Seed DoI credentials
for product, creds in CREDENTIALS_DOI.items():
    required_keys = PRODUCT_METADATA_DOI[product]["required_credentials"]
    filtered_creds = {k: v for k, v in creds.items() if k in required_keys}

    try:
        upsert_credential(
            db_name=DB_NAME,
            table="DoI_connector_credentials",
            userid=dummy_userid,
            uuid=dummy_uuid,
            username=dummy_username,
            name=product,
            credentials=filtered_creds,
            metadata=json.dumps(PRODUCT_METADATA_DOI[product])
        )
        print(f"✅ Inserted DoI {product}")
    except ValueError as ve:
        print(f"❌ Skipped DoI {product}: {ve}")