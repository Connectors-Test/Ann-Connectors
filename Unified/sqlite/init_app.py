from dotenv import load_dotenv
import os
import sqlite3
import json
from modules import *

load_dotenv()

# Credentials for app connectors
APP_CREDENTIALS = {
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
        "uid": os.getenv("ODOO_UID"),
        "key": os.getenv("ODOO_KEY")
    },
    "servicenow": {
        "instance": os.getenv("SERVICENOW_INSTANCE"),
        "username": os.getenv("SERVICENOW_USER"),
        "password": os.getenv("SERVICENOW_PASS")
    },
    "sap": {
        # "client": os.getenv("SAP_CLIENT"),
        # "user": os.getenv("SAP_USER"),
        # "password": os.getenv("SAP_PASSWORD"),
        # "host": os.getenv("SAP_HOST"),
        # "port": os.getenv("SAP_PORT")
        "api_key": os.getenv("SAP_SANDBOX_APIKEY")
    },
    "hubspot": {
        "access_token": os.getenv("HUBSPOT_ACCESS_TOKEN")
    }
}

# Metadata for each app connector
APP_METADATA = {
    "freshworks": {
        "description": "Freshworks API access for app integration.",
        "required_credentials": ["api_key", "domain"],
        "required_parameters": ["credentials", "endpoint", "params"],
        "query_type": "REST API",
        "example_query": "/api/v2/contacts",
        "method": "GET"
    },
    "zoho": {
        "description": "Zoho CRM API access.",
        "required_credentials": ["client_id", "client_secret", "refresh_token", "organization_id"],
        "required_parameters": ["credentials", "endpoint", "params"],
        "query_type": "REST API",
        "example_query": "/contacts?limit=10",
        "method": "GET"
    },
    "odoo": {
        "description": "Odoo XML-RPC or REST API access.",
        "required_credentials": ["url", "db", "uid", "key"],
        "required_parameters": ["credentials", "endpoint", "params"],
        "query_type": "XML-RPC/REST",
        "example_query": "/api/res.partner",
        "method": "POST"
    },
    "servicenow": {
        "description": "ServiceNow REST API access.",
        "required_credentials": ["instance", "username", "password"],
        "required_parameters": ["credentials", "endpoint", "params"],
        "query_type": "REST API",
        "example_query": "/api/now/table/incident",
        "method": "GET"
    },
    "sap": {
        "description": "SAP S/4HANA API access.",
        "required_credentials": ["api_key"], # "client", "user", "password", "host", "port"],
        "required_parameters": ["credentials", "endpoint", "params"],
        "query_type": "OData/API",
        "example_query": "/sap/opu/odata/sap/API_SALES_ORDER",
        "method": "GET"
    },
    "hubspot": {
        "description": "HubSpot API access.",
        "required_credentials": ["access_token"],
        "required_parameters": ["credentials", "endpoint", "params"],
        "query_type": "REST API",
        "example_query": "/crm/v3/objects/contacts",
        "method": "GET"
    }
}

DB_NAME = "wwwsmart_credentials.db"
conn = sqlite3.connect(DB_NAME)
conn.close()

# Create the new table for app connectors
create_table(DB_NAME, "App_connector_credentials")

import uuid

dummy_userid = str(uuid.uuid4())
dummy_uuid = "user_001"
dummy_username = "testuser"

for app, creds in APP_CREDENTIALS.items():
    required_keys = APP_METADATA[app]["required_credentials"]
    filtered_creds = {k: v for k, v in creds.items() if k in required_keys}

    try:
        upsert_credential(
            db_name=DB_NAME,
            table="App_connector_credentials",
            userid=dummy_userid,
            uuid=dummy_uuid,
            username=dummy_username,
            name=app,
            credentials=filtered_creds,
            metadata=json.dumps(APP_METADATA[app])
        )
        print(f"✅ Inserted {app}")
    except ValueError as ve:
        print(f"❌ Skipped {app}: {ve}")