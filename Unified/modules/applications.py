import requests

def fetch_from_freshworks(creds, app_type, endpoint, params=None, method=None):
    """
    Fetch data from any Freshworks apps (Freshdesk, Freshsales, etc.).
    creds: {
        "domain": str,      # e.g., "company.freshdesk.com"
        "api_key": str       # API key for the product
    }
    app_type: str, e.g., "freshdesk", "freshsales" (used to select base URL or headers)
    endpoint: str, API endpoint after base URL
    params: dict, optional query parameters or POST body
    method: "GET" or "POST"; if None, auto-decided
    scope: optional, reserved for future product-specific needs
    """
    if params is None:
        params = {}

    try:
        # Base URLs per app type
        base_urls = {
            "freshdesk": f"https://{creds['domain'].rstrip('/')}/api/v2/",
            "freshsales": f"https://{creds['domain'].rstrip('/')}/api/sales/"
            # add other Freshworks apps here
        }

        if app_type not in base_urls:
            return {"status": "error", "message": f"Unsupported Freshworks app: {app_type}"}

        url = f"{base_urls[app_type]}{endpoint.lstrip('/')}"

        # Headers
        headers = {"Authorization": f"Token token={creds['api_key']}", "Content-Type": "application/json"}

        # Decide HTTP method
        if not method:
            method = "POST" if endpoint.lower().startswith(("tickets", "query")) else "GET"
        method = method.upper()

        # Make request
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=params)
        else:
            return {"status": "error", "message": f"Unsupported HTTP method: {method}"}

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as he:
        return {"status": "error", "message": f"HTTP error: {str(he)}", "details": response.text}
    except Exception as e:
        return {"status": "error", "message": f"Freshworks fetch failed: {str(e)}"}


def fetch_from_zoho(creds, app_type, endpoint, params=None):
    """
    Fetch data from any Zoho application using refresh token.
    
    creds: {
        "client_id": str,
        "client_secret": str,
        "refresh_token": str, (Ensure it has the correct scope as needed for the target app)
        "organization_id": str (optional)
    }
    
    app_type: str, e.g., "crm", "books", "projects", "desk", "creator"
    endpoint: str, full API endpoint after base URL
    params: dict, optional query parameters
    """
    if params is None:
        params = {}

    try:
        # Refresh access token
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

        org_id = creds.get("organization_id")

        # Determine base URL per app
        base_urls = {
            "crm": "https://www.zohoapis.in/crm/v2/",
            "books": "https://books.zoho.in/api/v3/",
            "projects": "https://projectsapi.zoho.in/restapi/",
            "desk": "https://desk.zoho.in/api/v1/",
            "creator": "https://creator.zoho.in/api/v2/"
        }
        if app_type not in base_urls:
            return {"status": "error", "message": f"Unsupported Zoho app_type: {app_type}"}

        url = f"{base_urls[app_type]}{endpoint.lstrip('/')}"

        # Prepare headers
        headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
        if app_type in ["books", "projects"] and org_id:
            # Some apps require org ID in headers instead of params
            headers["X-com-zoho-books-organizationid"] = org_id
        elif app_type == "crm" and org_id:
            params["organization_id"] = org_id

        # Make request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        return {"status": "error", "message": f"Zoho fetch failed: {str(e)}"}

def fetch_from_odoo(creds, model, method, args=None, kwargs=None):
    """
    Fetch data from Odoo using JSON-RPC.
    creds: {
        "url": str,       # Odoo base URL
        "db": str,        # Database name
        "uid": int,       # User ID
        "key": str        # User API key/password
    }
    model: Odoo model name (e.g., 'res.partner')
    method: Odoo model method (e.g., 'search_read')
    args: list of positional arguments for the method
    kwargs: dict of keyword arguments for the method
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "id": 1,
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                creds["db"],
                creds["uid"],
                creds["key"],
                model,
                method,
                args or [],
                kwargs or {}
            ]
        }
    }
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(f"{creds['url'].rstrip('/')}/jsonrpc", json=payload, headers=headers)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "message": f"Odoo fetch failed: {str(e)}"}

def fetch_from_servicenow(creds, endpoint, params=None):
    """Fetch data from ServiceNow REST API."""
    if params is None:
        params = {}

    try:
        base_url = f"{creds['instance'].rstrip('/')}"
        # Ensure endpoint starts with /api/now/
        endpoint_path = endpoint.lstrip('/')
        if not endpoint_path.startswith("api/now/"):
            endpoint_path = f"api/now/{endpoint_path}"
        url = f"{base_url}/{endpoint_path}"

        auth = (creds["username"], creds["password"])
        headers = {"Content-Type": "application/json"}

        response = requests.get(url, headers=headers, params=params, auth=auth)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()
    except Exception as e:
        return {"status": "error", "message": f"ServiceNow fetch failed: {str(e)}"}

def fetch_from_sap(creds, producttype, subproducttype, field=None, filters=None):
    """
    Fetch data from SAP S/4HANA API using APIKey from environment.
    
    producttype: str - top-level category (e.g., 'product', 'sales')
    subproducttype: str - service endpoint key (e.g., 'API_PRODUCT_SRV')
    field: str (optional) - specific field/entity to fetch
    filters: str (optional) - OData $filter string
    """
    SAP_ENDPOINTS = {
        "product": {
            "API_PRODUCT_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_PRODUCT_SRV",
            "API_PRODUCT_STOCK_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_PRODUCT_STOCK_SRV"
        },
        "sales": {
            "API_SALES_CONTRACT_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_SALES_CONTRACT_SRV",
            "API_SALES_ORDER_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_SALES_ORDER_SRV"
        }
        # Add more categories
    }
    base_url = SAP_ENDPOINTS.get(producttype, {}).get(subproducttype)
    if not base_url:
        return {"status": "error", "message": "Unknown product/subproduct"}, 404

    url = base_url.rstrip("/") + (f"/{field}" if field else "")
    headers = {
        "APIKey": creds["api_key"],
        "Accept": "application/json"
    }
    params = {"$filter": filters} if filters else {}

    try:
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json(), r.status_code
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"SAP fetch failed: {str(e)}"}, 500
    
def fetch_from_hubspot(creds, app_type, endpoint, params=None, method="GET"):
    base_url = "https://api.hubapi.com"
    headers = {"Authorization": f"Bearer {creds['access_token']}"}
    
    url_map = {
        "contacts": "/crm/v3/objects/contacts",
        "companies": "/crm/v3/objects/companies",
        "deals": "/crm/v3/objects/deals",
        "tickets": "/crm/v3/objects/tickets",
    }
    
    url = f"{base_url}{url_map.get(app_type,'')}"
    if endpoint == "search":
        url += "/search"
    
    resp = requests.request(method, url, headers=headers, json=params if method=="POST" else None, params=params if method=="GET" else None)
    return resp.json()