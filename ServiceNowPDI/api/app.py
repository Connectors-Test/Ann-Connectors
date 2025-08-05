import os
import requests
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

BASE = os.getenv("SERVICENOW_INSTANCE")
AUTH = (os.getenv("SERVICENOW_USER"), os.getenv("SERVICENOW_PASS"))

# === 1. UNIVERSAL Data Proxy ===
@app.route("/api/data/<path:endpoint>", methods=["GET"])
def dynamic_proxy(endpoint):
    query_string = request.query_string.decode("utf-8")
    url = f"{BASE}/api/now/{endpoint}"
    if query_string:
        url += f"?{query_string}"
    try:
        res = requests.get(url, auth=AUTH)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === 2. Schema Generator ===
@app.route("/schema/<path:endpoint>", methods=["GET"])
def get_schema(endpoint):
    url = f"{BASE}/api/now/{endpoint}?sysparm_limit=1"
    try:
        res = requests.get(url, auth=AUTH)
        data = res.json()
    except Exception as e:
        return jsonify({"error": "Failed to fetch or parse", "details": str(e)}), 500

    result = data.get("result")
    if isinstance(result, list) and result:
        sample = result[0]
    elif isinstance(result, dict):
        sample = result
    else:
        return jsonify({"error": "Unexpected structure"}), 500

    schema = {k: type(v).__name__ for k, v in sample.items()}
    return jsonify(schema)

# === 3. Auth Status Check ===
@app.route("/auth", methods=["GET"])
def auth_status():
    test_url = f"{BASE}/api/now/table/incident?sysparm_limit=1"
    res = requests.get(test_url, auth=AUTH)
    if res.status_code == 200:
        return jsonify({"auth": "success"})
    else:
        return jsonify({"auth": "failed", "status": res.status_code})

# === 4. List Sub Types ===
@app.route("/listsubproducttype/<path:producttype>", methods=["GET"])
def list_subtypes(producttype):
    # Build the URL dynamically
    url = f"{BASE}/api/now/{producttype}?sysparm_limit=1"
    try:
        res = requests.get(url, auth=AUTH)
        data = res.json()
    except Exception as e:
        return jsonify({"error": "Request failed", "details": str(e)}), 500

    result = data.get("result")
    if isinstance(result, list) and result:
        sample = result[0]
    elif isinstance(result, dict):
        sample = result
    else:
        return jsonify({"error": "No fields found"}), 404

    return jsonify({"fields": list(sample.keys())})

# === 5. Root ===
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "ServiceNow API Proxy working",
        "routes": [
            "/api/data/<path:endpoint>?<query>",
            "/schema/<path:endpoint>",
            "/auth",
            "/listsubproducttype"
        ]
    })
