from dotenv import load_dotenv
import os
import sqlite3
import json
from ..modules import *

load_dotenv()

# Credentials for ecom connectors
CREDENTIALS = {
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

# Metadata for each ecom connector
PRODUCT_METADATA = {
    "zoho": {
        "description": "Zoho CRM API access for e-commerce integration.",
        "required_credentials": ["client_id", "client_secret", "refresh_token"],
        "required_parameters": ["credentials", "endpoint", "params"],
        "query_type": "REST API",
        "example_query": "/contacts?limit=10",
        "method": "GET"
    },
    "wix": {
        "description": "wix e-commerce platform API access.",
        "required_credentials": ["api_key", "account_id", "site_id"],
        "required_parameters": ["credentials", "endpoint", "params"],
        "query_type": "REST API",
        "example_query": "/orders?status=paid",
        "method": "GET"
    },
    "woocommerce": {
        "description": "WooCommerce REST API connection.",
        "required_credentials": ["url", "consumer_key", "consumer_secret"],
        "required_parameters": ["credentials", "endpoint", "params"],
        "query_type": "REST API",
        "example_query": "/wp-json/wc/v3/orders?per_page=10",
        "method": "GET"
    },
    "shopify": {
        "description": "Shopify REST API connection.",
        "required_credentials": ["store_url", "access_token"],
        "required_parameters": ["credentials", "endpoint", "params"],
        "query_type": "REST API",
        "example_query": "/admin/api/2025-01/orders.json?limit=10",
        "method": "GET"
    }
}

DB_NAME = "Unified/sqlite/wwwsmart_credentials.db"
conn = sqlite3.connect(DB_NAME)
conn.close()

create_table(DB_NAME, "Ecom_connector_credentials")

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
            table="Ecom_connector_credentials",
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