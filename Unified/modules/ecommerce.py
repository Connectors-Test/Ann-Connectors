import requests
from flask import jsonify

def fetch_from_zoho(creds, endpoint, params=None):
    """
    Fetch data from Zoho CRM API using refresh token.

    creds: {
        "client_id": str,
        "client_secret": str,
        "refresh_token": str,
        "organization_id": str (optional)
    }
    endpoint: API endpoint, e.g., "Leads"
    params: optional query parameters (dict)
    """
    try:
        if params is None:
            params = {}

        # 1. Get a new access token using refresh token
        token_url = "https://accounts.zoho.in/oauth/v2/token"
        token_data = {
            "grant_type": "refresh_token",
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "refresh_token": creds["refresh_token"]
        }
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]

        # 2. Add organization_id if present
        org_id = creds.get("organization_id")
        if org_id:
            params["organization_id"] = org_id

        # 3. Make the actual API request
        url = f"https://www.zohoapis.in/crm/v2/{endpoint.lstrip('/')}"
        headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        return {"status": "error", "message": f"Zoho fetch failed: {str(e)}"}

def fetch_from_wix(creds, endpoint, params=None, scope=None):
    """
    Fetch data from Wix API with automatic ID handling.

    Args:
        creds (dict): {'api_key': '...', 'site_id': '...', 'account_id': '...'}
        endpoint (str): Wix API endpoint, e.g., "stores/v1/products/params"
        params (dict, optional): Parameters to send with the request
        scope (str, optional): "site" or "account", determines which ID header to include
    """
    if params is None:
        params = {}

    url = f"https://www.wixapis.com/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {creds['api_key']}",
        "Content-Type": "application/json"
    }

    # Add the correct ID header automatically
    if scope == "site" and creds["site_id"]:
        headers["wix-site-id"] = creds["site_id"]
    elif scope == "account" and creds["account_id"]:
        headers["wix-account-id"] = creds["account_id"]
    
    try:
        if "/query" in endpoint:  # POST endpoints
            response = requests.post(url, headers=headers, json=params)
        else:  # GET endpoints
            response = requests.get(url, headers=headers, params=params)

        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "error", "message": f"Wix fetch failed: {str(e)}"}

def fetch_from_woocommerce(creds, endpoint, params=None):
    """
    creds: { 'url': str, 'consumer_key': str, 'consumer_secret': str }
    endpoint: WooCommerce API endpoint (e.g. 'products', 'orders')
    params: dict of query params
    """
    try:
        base_url = creds['url'].rstrip('/')
        url = f"{base_url}/wp-json/wc/v3/{endpoint.lstrip('/')}"
        if params is None:
            params = {}

        # Add creds in query (alternative auth method)
        params.update({
            'consumer_key': creds['consumer_key'],
            'consumer_secret': creds['consumer_secret']
        })

        resp = requests.get(
            url,
            params=params,
            timeout=10,
            verify=False   # allow insecure (like curl -k)
        )
        resp.raise_for_status()
        return resp.json()

    except Exception as e:
        return {"message": f"WooCommerce fetch failed: {str(e)}", "status": "error"}

def fetch_from_shopify(creds, endpoint, params=None):
    """Fetch data from Shopify REST API."""
    try:
        if params is None:
            params = {}
        url = f"https://{creds['store_url'].rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {"X-Shopify-Access-Token": creds['access_token']}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "error", "message": f"Shopify fetch failed: {str(e)}"}