import os
from dotenv import load_dotenv

load_dotenv()

# ==========================
# Flask App Config
# ==========================
FLASK_CONFIG = {
    "DEBUG": os.getenv("FLASK_DEBUG", "True") == "True",
    "HOST": os.getenv("FLASK_HOST", "0.0.0.0"),
    "PORT": int(os.getenv("FLASK_PORT", 5000))
}


# ==========================
# Application Connectors (App)
# ==========================
APP_CONFIG = {
    "freshworks": {
        "api_key": os.getenv("FRESHDESK_API_KEY"),
        "domain": os.getenv("FRESHDESK_DOMAIN")
    },
    "zoho": {
        "client_id": os.getenv("ZOHO_CLIENT_ID"),
        "client_secret": os.getenv("ZOHO_CLIENT_SECRET"),
        "refresh_token": os.getenv("ZOHO_REFRESH_TOKEN"),
        "organization_id": os.getenv("ZOHO_ORGANIZATION_ID")
    },
    "odoo": {
        "url": os.getenv("ODOO_URL"),
        "db": os.getenv("ODOO_DB"),
        "uid": int(os.getenv("ODOO_UID", 2)),
        "key": os.getenv("ODOO_KEY")
    },
    "servicenow": {
        "instance": os.getenv("SERVICENOW_INSTANCE"),
        "user": os.getenv("SERVICENOW_USER"),
        "password": os.getenv("SERVICENOW_PASS")
    },
    "sap": {
        "sandbox_apikey": os.getenv("SAP_SANDBOX_APIKEY")
    },
    "hubspot": {
        "access_token": os.getenv("HUBSPOT_ACCESS_TOKEN")
    }
}

# ==========================
# Database Connectors (db)
# ==========================
DB_CONFIG = {
    "databricks": {
        "host": os.getenv("DATABRICKS_HOST_NAME"),
        "token": os.getenv("DATABRICKS_TOKEN"),
        "warehouse_id": os.getenv("DATABRICKS_WAREHOUSE_ID")
    },
    "postgresql": {
        "host": os.getenv("PG_HOST"),
        "port": int(os.getenv("PG_PORT", 5432)),
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
        "port": int(os.getenv("MYSQL_PORT", 3306)),
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
        "database": os.getenv("NEO4J_DATABASE", "neo4j")
    }
}


# ==========================
# Devops & IoT Connectors (DOI)
# ==========================
DOI_CONFIG = {
    "clickhouse": {
        "url": os.getenv("CLICKHOUSE_URL"),
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
        "port": int(os.getenv("TS_PORT", 5432)),
        "user": os.getenv("TS_USER"),
        "password": os.getenv("TS_PASSWORD"),
        "database": os.getenv("TS_DATABASE"),
        "sslmode": os.getenv("TS_SSLMODE", "prefer")
    },
    "redis": {
        "host": os.getenv("REDIS_HOST"),
        "port": int(os.getenv("REDIS_PORT", 6379)),
        "user": os.getenv("REDIS_USER", "default"),
        "password": os.getenv("REDIS_PASS")
    },
    "elasticsearch": {
        "cloud_id": os.getenv("ES_CLOUD_ID"),
        "username": os.getenv("ES_USERNAME"),
        "password": os.getenv("ES_PASSWORD"),
        "default_index": os.getenv("ES_DEFAULT_INDEX", "logs-*")
    },
    "opensearch": {
        "host": os.getenv("OS_HOST"),
        "username": os.getenv("OS_USERNAME"),
        "password": os.getenv("OS_PASSWORD")
    }
}

# ==========================
# E-commerce Connectors (Ecom)
# ==========================
ECOM_CONFIG = {
    "zoho": {
        "client_id": os.getenv("ZOHO_CLIENT_ID"),
        "client_secret": os.getenv("ZOHO_CLIENT_SECRET"),
        "refresh_token": os.getenv("ZOHO_REFRESH_TOKEN")
    },
    "wix": {
        "api_key": os.getenv("WIX_API_KEY"),
        "account_id": os.getenv("WIX_ACCOUNT_ID"),
        "site_id": os.getenv("WIX_SITE_ID")
    },
    "woocommerce": {
        "url": os.getenv("WC_URL"),
        "consumer_key": os.getenv("WC_CONSUMER_KEY"),
        "consumer_secret": os.getenv("WC_CONSUMER_SECRET")
    },
    "shopify": {
        "store_url": os.getenv("SHOPIFY_STORE_URL"),
        "access_token": os.getenv("SHOPIFY_ACCESS_TOKEN")
    }
}

# ==========================
# Spreadsheet Connectors (ss)
# ==========================
SS_CONFIG = {
    "googlesheet": {
        "sheet_id": os.getenv("GOOGLE_SHEET_ID")
    }
}
