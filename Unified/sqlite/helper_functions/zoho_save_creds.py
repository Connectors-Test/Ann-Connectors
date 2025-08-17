import requests
import json
from modules import upsert_credential
from dotenv import load_dotenv
import os

load_dotenv()

ZOHO_BASE = os.getenv("ZOHO_BASE_URL")
REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI")
CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ORG_ID = os.getenv("ZOHO_ORGANIZATION_ID")

def save_zoho_tokens(db_name, userid, uuid, username, code):
    """
    Exchange authorization code for refresh token and save to DB.
    """
    url = f"{ZOHO_BASE}/oauth/v2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }

    r = requests.post(url, data=data)
    r.raise_for_status()
    tokens = r.json()

    if "refresh_token" not in tokens:
        raise Exception(f"Zoho did not return a refresh_token: {tokens}")

    creds = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": tokens["refresh_token"]
    }

    upsert_credential(
        db_name=db_name,
        table="Ecom_connector_credentials",
        userid=userid,
        uuid=uuid,
        username=username,
        name="zoho",
        credentials=creds,
        metadata=json.dumps({
            "description": "Zoho CRM API access for e-commerce integration.",
            "required_credentials": ["client_id", "client_secret", "refresh_token"],
            "required_parameters": ["credentials", "endpoint", "params"],
            "query_type": "REST API",
            "example_query": "/contacts?limit=10",
            "method": "GET"
        })
    )

    return creds