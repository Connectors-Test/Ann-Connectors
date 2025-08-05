from flask import Flask, request, jsonify
import requests, os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

SAP_API_KEY = os.getenv("SAP_SANDBOX_APIKEY")

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

@app.route("/")
def home():
    return jsonify({"status": "SAP Flask API is running"})

@app.route("/api/data/<producttype>/<subproducttype>", methods=["GET"])
@app.route("/api/data/<producttype>/<subproducttype>/<field>", methods=["GET"])
def get_data(producttype, subproducttype, field=None):

    base_url = SAP_ENDPOINTS.get(producttype, {}).get(subproducttype)
    if not base_url:
        return jsonify({"error": "Unknown product/subproduct"}), 404

    query = request.args.get("filters", "")
    url = base_url.rstrip("/") + (f"/{field}" if field else "")
    headers = {"APIKey": SAP_API_KEY, "Accept": "application/json"}

    r = requests.get(url, headers=headers, params={"$filter": query} if query else {})
    return jsonify(r.json()), r.status_code

@app.route("/api/schema/<producttype>/<subproducttype>", methods=["GET"])
def get_schema(producttype, subproducttype):

    base_url = SAP_ENDPOINTS.get(producttype, {}).get(subproducttype)
    if not base_url:
        return jsonify({"error": "Invalid endpoint"}), 404

    metadata_url = base_url.rstrip("/") + "/$metadata"
    headers = {"APIKey": SAP_API_KEY}
    r = requests.get(metadata_url, headers=headers)
    return jsonify({"schema_xml": r.text}), r.status_code

@app.route("/api/listsubtypes/<producttype>", methods=["GET"])
def list_subtypes(producttype):

    subtypes = list(SAP_ENDPOINTS.get(producttype, {}).keys())
    return jsonify({"subproducttypes": subtypes})

@app.route("/auth", methods=["GET"])
def auth_check():
    test_url = SAP_ENDPOINTS.get("product", {}).get("API_PRODUCT_SRV")
    if not test_url:
        return jsonify({"error": "Missing test endpoint"}), 500

    headers = {
        "APIKey": SAP_API_KEY,
        "Accept": "application/json"
    }

    try:
        r = requests.get(test_url.rstrip("/") + "/A_Product?$top=1", headers=headers)
        if r.status_code == 200:
            return jsonify({"status": "Connected to SAP Sandbox successfully"}), 200
        else:
            return jsonify({
                "error": f"SAP responded with status {r.status_code}",
                "details": r.text[:300]
            }), r.status_code
    except Exception as e:
        return jsonify({
            "error": "Exception during auth check",
            "message": str(e)
        }), 500

application = app