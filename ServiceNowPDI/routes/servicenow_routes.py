import os
import requests
from flask import Blueprint, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

servicenow_bp = Blueprint('servicenow_bp', __name__)

BASE = os.getenv("SERVICENOW_INSTANCE")
AUTH = (os.getenv("SERVICENOW_USER"), os.getenv("SERVICENOW_PASS"))

ENDPOINTS = {
"Incidents": "/api/now/table/incident",
"Specific Incident": "/api/now/table/incident/1c741bd70b2322007518478d83673af3",
"Active Users": "/api/now/table/sys_user?sysparm_query=active=true",
"Incident Count": "/api/now/stats/incident?sysparm_count=true",
"Import Table": "/api/now/import/u_test_import",
"All Attachments": "/api/now/attachment",
"Specific Attachment Meta": "/api/now/attachment/003a3ef24ff1120031577d2ca310c74b",
"Specific Attachment File": "/api/now/attachment/003a3ef24ff1120031577d2ca310c74b/file",
"All Users": "/api/now/table/sys_user",
"User Count": "/api/now/stats/sys_user?sysparm_count=true",
"User Meta": "/api/now/ui/meta/sys_user",
"Catalog Items": "/api/sn_sc/servicecatalog/items",
"CMDB CIs": "/api/now/table/cmdb_ci"
}

@servicenow_bp.route("/api/<key>")
def proxy(key):
    path = ENDPOINTS.get(key)
    if not path:
        return jsonify({"error": "Invalid key"}), 404
    url = f"{BASE}{path}"
    if '?' not in path:
        url = f"{BASE}{path}?sysparm_limit=10"
    else:
        url = f"{BASE}{path}&sysparm_limit=5"
    r = requests.get(url, auth=AUTH)
    return jsonify(r.json())

# @servicenow_bp.route("/links")
# def list_routes():
#     # Expose links for frontend
#     route_map = {k: f"/api/{k}" for k in ENDPOINTS}
#     return render_template("index.html", routes=route_map)

@servicenow_bp.route("/links")
def list_routes():
    grouped = {
        "Incidents": {
            "All Incidents": "Incidents",
            "Specific Incident": "Specific Incident",
            "Incident Count": "Incident Count",
        },
        "Users": {
            "All Users": "All Users",
            "Active Users": "Active Users",
            "User Count": "User Count",
            "User Meta": "User Meta",
        },
        "Attachments": {
            "All Attachments": "All Attachments",
            "Attachment Meta": "Specific Attachment Meta",
            "Attachment File": "Specific Attachment File",
        },
        "Catalog / Config": {
            "Catalog Items": "Catalog Items",
            "CMDB CIs": "CMDB CIs",
        },
        "Import": {
            "Import Table": "Import Table"
        }
    }
    route_map = {k: f"/api/{k}" for k in ENDPOINTS}
    return render_template("index.html", grouped=grouped, routes=route_map)