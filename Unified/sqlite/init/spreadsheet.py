from dotenv import load_dotenv
import os
import sqlite3
from ..modules import *

load_dotenv()

CREDENTIALS = {
    "googlesheet": {
        "sheet_id": os.getenv("GOOGLE_SHEET_ID")
    }
}

# Metadata for LLM training
PRODUCT_METADATA = {
    "googlesheet": {
        "description": "Google Sheets using gviz/tq query.",
        "required_credentials": ["sheet_id"],
        "required_parameters": ["credentials", "query"],
        "query_type": "Google Visualization Query Language",
        "example_query": "select A, B, C where A > 10"
    }
}

DB_NAME = "Unified/sqlite/wwwsmart_credentials.db"
conn = sqlite3.connect(DB_NAME)
conn.close()

create_table(DB_NAME, "SS_connector_credentials")

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
            table="SS_connector_credentials",
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
