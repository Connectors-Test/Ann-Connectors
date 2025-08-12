from flask import Flask, request, jsonify
from sqlite_loader import *
from modules.databases import *
from modules.spreadsheet import *

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

@app.route("/query/db/<productType>", methods=["GET"])
def db_query_data(productType):
    query = request.args.get("query")
    userid = request.args.get("userid")

    if not query:
        return jsonify({"status": "error", "message": "query parameter is required"}), 400

    # Fetch credentials dynamically based on userid or fallback
    if userid:
        creds_entry = fetch_db_credentials(user_id=userid)
        # fetch_db_credentials should return either a single dict or list, handle accordingly
        if isinstance(creds_entry, list):
            creds_entry = next((item for item in creds_entry if item['name'].lower() == productType.lower()), None)
    else:
        creds_list = fetch_db_credentials()
        creds_entry = next((item for item in creds_list if item['name'].lower() == productType.lower()), None)

    if not creds_entry:
        return jsonify({"status": "error", "message": "Invalid productType"}), 400

    creds = creds_entry['credentials']

    try:
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
            query = request.args.get("query", "SELECT 1")
            table = request.args.get("table")
            return fetch_from_mysql(creds, query, table)
        
        elif productType.lower() == "mongodb":
            query = request.args.get("query")
            collection = request.args.get("collection")
            database = request.args.get("database")
            return fetch_from_mongodb(creds, query, collection, database)

        elif productType.lower() == "snowflake":
            query = request.args.get("query")
            table = request.args.get("table")
            database = request.args.get("database")
            schema = request.args.get("schema")
            return fetch_from_snowflake(creds, query, table, database, schema)

        elif productType.lower() == "airtable":
            table = request.args.get("table")
            query_raw = request.args.get("query")
            return fetch_from_airtable(creds, table, query_raw)
        
        else:
            return jsonify({"status": "error", "message": "Unsupported productType"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/query/ss/<productType>", methods=["GET"])
def ss_query_data(productType):
    query = request.args.get("query")
    userid = request.args.get("userid")

    if not query:
        return jsonify({"status": "error", "message": "query parameter is required"}), 400

    # Fetch credentials dynamically based on userid or fallback
    if userid:
        creds_entry = fetch_ss_credentials(user_id=userid)
        if isinstance(creds_entry, list):
            creds_entry = next((item for item in creds_entry if item['name'].lower() == productType.lower()), None)
    else:
        creds_list = fetch_ss_credentials()
        creds_entry = next((item for item in creds_list if item['name'].lower() == productType.lower()), None)

    if not creds_entry:
        return jsonify({"status": "error", "message": "Invalid productType"}), 400

    creds = creds_entry['credentials']

    try:
        if productType.lower() == "googlesheet":
            query = request.args.get("query", "SELECT *")
            return fetch_from_googlesheet(creds, query)

        else:
            return jsonify({"status": "error", "message": "Unsupported productType"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/metadata", methods=["GET"])
def get_metadata():
    db_creds = fetch_db_credentials()
    product_type = request.args.get("productType")

    if product_type:
        for db in db_creds:
            if db["name"].lower() == product_type.lower():
                return jsonify({"status": "success", "data": db["metadata"]})
        return jsonify({"status": "error", "message": "Invalid productType"}), 400

    # Return metadata for all product types
    all_metadata = {
        db["name"]: db["metadata"] for db in db_creds
    }
    return jsonify({"status": "success", "data": all_metadata})

if __name__ == "__main__":
    app.run(debug=True)