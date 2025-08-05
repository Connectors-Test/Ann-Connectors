import os
import requests
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BASE = os.getenv("SERVICENOW_INSTANCE")
AUTH = (os.getenv("SERVICENOW_USER"), os.getenv("SERVICENOW_PASS"))

# === Hardcoded mock map for now ===
ENDPOINTS = {
    "incident": ["default", "1c741bd70b2322007518478d83673af3"],
    "sys_user": ["active", "meta", "count"],
    "attachment": ["all", "meta", "file"],
    "u_test_import": ["import"],
    "cmdb_ci": ["all"],
    "sn_sc/servicecatalog/items": ["all"]
}

# === 1. Get Data ===
@app.route("/api/data/<product>/<subproduct>", methods=["GET"])
def get_data(product, subproduct):
    # Handle nested service path like "sn_sc/servicecatalog/items"
    service_path = f"{product}/{subproduct}" if '/' in product else subproduct

    path = f"/api/now/table/{service_path}"
    if product == "sn_sc":
        path = f"/api/{product}/{subproduct}"

    url = f"{BASE}{path}?sysparm_limit=10"
    res = requests.get(url, auth=AUTH)
    return jsonify(res.json())

# === 2. Get JSON Schema ===
@app.route("/schema/<product>/<subproduct>", methods=["GET"])
def get_schema(product, subproduct):
    service_path = f"{product}/{subproduct}" if '/' in product else subproduct

    path = f"/api/now/table/{service_path}"
    if product == "sn_sc":
        path = f"/api/{product}/{subproduct}"

    url = f"{BASE}{path}?sysparm_limit=1"
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

# === 3. List Subproduct Types ===
@app.route("/listsubproducttype", methods=["GET"])
def list_subproducttype():
    return jsonify(ENDPOINTS)

# === 4. Auth Status Check ===
@app.route("/auth", methods=["GET"])
def auth_status():
    test_url = f"{BASE}/api/now/table/incident?sysparm_limit=1"
    res = requests.get(test_url, auth=AUTH)
    if res.status_code == 200:
        return jsonify({"auth": "success"})
    else:
        return jsonify({"auth": "failed", "status": res.status_code})

# === 5. Root ===
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "ServiceNow Minimal API",
        "routes": [
            "/api/data/<product>/<subproduct>",
            "/schema/<product>/<subproduct>",
            "/listsubproducttype",
            "/auth"
        ]
    })
