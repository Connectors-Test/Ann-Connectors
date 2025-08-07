from flask import Flask, request, jsonify
import requests
import psycopg2
import mysql.connector
from pymongo import MongoClient
import snowflake.connector
from sqlite_loader import *
import json
from sqlite_loader import fetch_api_credentials, fetch_db_credentials

db_creds = fetch_db_credentials()

print(db_creds)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "Unified API Proxy working",
        "routes": [
            "/query/<productType>",
            "/metadata"
        ]
    })

@app.route("/query/<productType>", methods=["GET"])
def query_data(productType):
    query = request.args.get("query")
    if not query:
        return jsonify({"status": "error", "message": "query parameter is required"}), 400

    # 🔍 Find credentials for the given productType
    creds_entry = next((item for item in db_creds if item['dbname'].lower() == productType.lower()), None)

    if not creds_entry:
        return jsonify({"status": "error", "message": "Invalid productType"}), 400

    creds = creds_entry['credentials']

    try:
        data = []

        if productType.lower() == "databricks":
            url = f"{creds['base_url']}/api/2.0/sql/statements"
            headers = {"Authorization": f"Bearer {creds['token']}"}
            payload = {"statement": query, "warehouse_id": "<WAREHOUSE_ID>"}
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()

        elif productType.lower() == "postgresql":
            conn = psycopg2.connect(
                host=creds["host"], port=creds["port"],
                user=creds["user"], password=creds["password"], database=creds["database"]
            )
            cur = conn.cursor()
            cur.execute(query)
            data = cur.fetchall()
            cur.close()
            conn.close()

        elif productType.lower() == "mysql":
            conn = mysql.connector.connect(
                host=creds["host"], port=creds["port"],
                user=creds["user"], password=creds["password"], database=creds["database"]
            )
            cur = conn.cursor()
            cur.execute(query)
            data = cur.fetchall()
            cur.close()
            conn.close()

        elif productType.lower() == "mongodb":
            client = MongoClient(creds["uri"])
            db = client[creds["database"]]
            data = list(db.command("eval", query)["retval"])
            client.close()

        elif productType.lower() == "snowflake":
            conn = snowflake.connector.connect(
                user=creds["user"], password=creds["password"], account=creds["account"],
                warehouse=creds["warehouse"], database=creds["database"], schema=creds["schema"]
            )
            cur = conn.cursor()
            cur.execute(query)
            data = cur.fetchall()
            cur.close()
            conn.close()

        elif productType.lower() == "airtable":
            url = f"https://api.airtable.com/v0/{creds['base_id']}/Table1"
            headers = {"Authorization": f"Bearer {creds['api_key']}"}
            params = {"filterByFormula": query}
            response = requests.get(url, headers=headers, params=params)
            data = response.json()

        elif productType.lower() == "googlesheet":
            url = f"{creds['sheet_url']}{query}"
            response = requests.get(url)
            if response.status_code == 200:
                text = response.text
                json_start = text.find("({") + 1
                json_end = text.rfind("})") + 1
                data = requests.utils.json.loads(text[json_start:json_end])
            else:
                return jsonify({"status": "error", "message": response.text}), response.status_code

        else:
            return jsonify({"status": "error", "message": "Unsupported productType"}), 400

        return jsonify({"status": "success", "data": data})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/metadata", methods=["GET"])
def get_metadata():
    db_creds = fetch_db_credentials()
    product_type = request.args.get("productType")

    if product_type:
        for db in db_creds:
            if db["dbname"].lower() == product_type.lower():
                return jsonify({"status": "success", "data": db["metadata"]})
        return jsonify({"status": "error", "message": "Invalid productType"}), 400

    # Return metadata for all product types
    all_metadata = {
        db["dbname"]: db["metadata"] for db in db_creds
    }
    return jsonify({"status": "success", "data": all_metadata})

if __name__ == "__main__":
    app.run(debug=True)