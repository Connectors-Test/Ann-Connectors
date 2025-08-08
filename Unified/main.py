from flask import Flask, request, jsonify
import requests
import psycopg2
import mysql.connector
from pymongo import MongoClient
import snowflake.connector
from sqlite_loader import fetch_db_credentials
from db_modules import *

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
    uuid = request.args.get("uuid")

    if not query:
        return jsonify({"status": "error", "message": "query parameter is required"}), 400

    # Fetch credentials dynamically based on uuid or fallback
    if uuid:
        creds_entry = fetch_db_credentials(uuid=uuid)
        # fetch_db_credentials should return either a single dict or list, handle accordingly
        if isinstance(creds_entry, list):
            creds_entry = next((item for item in creds_entry if item['dbname'].lower() == productType.lower()), None)
    else:
        creds_list = fetch_db_credentials()
        creds_entry = next((item for item in creds_list if item['dbname'].lower() == productType.lower()), None)

    if not creds_entry:
        return jsonify({"status": "error", "message": "Invalid productType"}), 400

    creds = creds_entry['credentials']

    try:
        data = []

        if productType.lower() == "databricks":    
            query = request.args.get("query", "SELECT 1")
            tableName = request.args.get("table")
            databaseName = request.args.get("database", "default")
            return fetch_from_databricks(creds, query, tableName, databaseName)

        elif productType.lower() == "postgresql":  
            query = request.args.get("query", "SELECT 1")
            table = request.args.get("table")
            return fetch_from_postgresql(creds, query, table)

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
            table = request.args.get("table")
            query_raw = request.args.get("query")
            return fetch_from_airtable(creds, table, query_raw)

        elif productType.lower() == "googlesheet":
            query = request.args.get("query", "SELECT *")
            return fetch_from_googlesheet(creds, query)
        
        else:
            return jsonify({"status": "error", "message": "Unsupported productType"}), 400

        return data

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