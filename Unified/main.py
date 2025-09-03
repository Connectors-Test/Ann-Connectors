from flask import Flask, request, jsonify
from sqlite_loader import *
from modules.databases import *
from modules.spreadsheet import *
from modules.devops_and_iot import *
from modules.ecommerce import *
from modules.applications import *

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
            return fetch_from_databricks(creds, query)

        elif productType.lower() == "postgresql":  
            return fetch_from_postgresql(creds, query)
        
        elif productType.lower() == "supabase":
            return fetch_from_supabase(creds, query)

        elif productType.lower() == "mysql":
            return fetch_from_mysql(creds, query)
        
        elif productType.lower() == "mongodb":
            collection = request.args.get("collection")
            database = request.args.get("database")
            return fetch_from_mongodb(creds, query, collection, database)

        elif productType.lower() == "snowflake":
            database = request.args.get("database")
            schema = request.args.get("schema")
            return fetch_from_snowflake(creds, query, database, schema)

        elif productType.lower() == "airtable":
            table = request.args.get("table")
            return fetch_from_airtable(creds, table, query)
        
        elif productType.lower() == "neo4j":
            return fetch_from_neo4j(creds, query)
        
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

@app.route("/query/doi/<productType>", methods=["GET"])
def doi_query_data(productType):
    # main query parameter — different DoI products may interpret it differently
    query = request.args.get("query")
    userid = request.args.get("userid")

    if not query:
        return jsonify({"status": "error", "message": "query parameter is required"}), 400

    # Fetch credentials dynamically
    if userid:
        creds_entry = fetch_doi_credentials(user_id=userid)
        if isinstance(creds_entry, list):
            creds_entry = next((item for item in creds_entry if item['name'].lower() == productType.lower()), None)
    else:
        creds_list = fetch_doi_credentials()
        creds_entry = next((item for item in creds_list if item['name'].lower() == productType.lower()), None)

    if not creds_entry:
        return jsonify({"status": "error", "message": "Invalid productType"}), 400

    creds = creds_entry['credentials']

    try:
        if productType.lower() == "clickhouse":
            # table = request.args.get("table")
            # database = request.args.get("database", creds.get("database", "default"))
            return fetch_from_clickhouse(creds, query)

        elif productType.lower() == "tempo":
            # Example: query_range param contains JSON body for trace search
            return fetch_from_tempo(creds, query)

        elif productType.lower() == "loki":
            # query is a LogQL string
            minutes = request.args.get("minutes", 5)
            return fetch_from_loki(creds, query, minutes)

        elif productType.lower() == "prometheus":
            # query is a PromQL string
            return fetch_from_prometheus(creds, query)

        elif productType.lower() == "influxdb":
            # query is a Flux query
            return fetch_from_influxdb(creds, query)

        elif productType.lower() == "timescaledb":
            # table = request.args.get("table")
            return fetch_from_timescaledb(creds, query)

        elif productType.lower() == "redis":
            # query is a Redis command, e.g., "LRANGE logs 0 10"
            args_str = request.args.get("args", "")
            return fetch_from_redis(creds, query, args_str)

        elif productType.lower() == "elasticsearch":
            # query param should be JSON DSL
            index = request.args.get("index", creds.get("default_index", "_all"))
            return fetch_from_elasticsearch(creds, query, index)
        
        elif productType.lower() == "opensearch":
            # query param should be JSON DSL
            index = request.args.get("index", "_all")
            dsl_query = json.loads(query)
            return fetch_from_opensearch(creds, dsl_query, index)

        else:
            return jsonify({"status": "error", "message": "Unsupported productType"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route("/query/ecom/<productType>", methods=["GET"])
def ecom_query_data(productType):
    endpoint = request.args.get("endpoint")
    params = request.args.get("params", "{}")
    userid = request.args.get("userid")
    scope = request.args.get("scope")

    if not endpoint:
        return jsonify({"status": "error", "message": "endpoint parameter is required"}), 400

    # Parse params if sent as JSON string
    try:
        params = json.loads(params)
    except:
        return jsonify({"status": "error", "message": "params must be a valid JSON string"}), 400

    # Fetch credentials dynamically based on userid or fallback
    if userid:
        creds_entry = fetch_ecom_credentials(user_id=userid)  # should return list/dict of ecom credentials
        if isinstance(creds_entry, list):
            creds_entry = next((item for item in creds_entry if item['name'].lower() == productType.lower()), None)
    else:
        creds_list = fetch_ecom_credentials()
        creds_entry = next((item for item in creds_list if item['name'].lower() == productType.lower()), None)

    if not creds_entry:
        return jsonify({"status": "error", "message": "Invalid productType"}), 400

    creds = creds_entry['credentials']

    try:
        if productType.lower() == "zoho":
            return fetch_from_zoho_crm(creds, endpoint, params)

        elif productType.lower() == "wix":
            return fetch_from_wix(creds, endpoint, params, scope)

        elif productType.lower() == "woocommerce":
            return fetch_from_woocommerce(creds, endpoint, params)

        elif productType.lower() == "shopify":
            return fetch_from_shopify(creds, endpoint, params)

        else:
            return jsonify({"status": "error", "message": "Unsupported productType"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/query/app/<productType>", methods=["GET"])
def app_query_data(productType):
    userid = request.args.get("userid")
    pt = productType.lower()

    # Fetch credentials dynamically based on userid or fallback
    if userid:
        creds_entry = fetch_app_credentials(user_id=userid)
        if isinstance(creds_entry, list):
            creds_entry = next((item for item in creds_entry if item['name'].lower() == pt), None)
    else:
        creds_list = fetch_app_credentials()
        creds_entry = next((item for item in creds_list if item['name'].lower() == pt), None)

    if not creds_entry:
        return jsonify({"status": "error", "message": "Invalid productType"}), 400

    creds = creds_entry['credentials']

    try:
        # Zoho
        if pt == "zoho":
            app_type = request.args.get("app_type", "crm")  # default to crm
            endpoint = request.args.get("endpoint")
            params = request.args.get("params", "{}")
            try:
                params = json.loads(params)
            except:
                return jsonify({"status": "error", "message": "params must be a valid JSON string"}), 400

            return fetch_from_zoho(creds, app_type, endpoint, params)

        # Freshworks
        elif pt == "freshworks":
            app_type = request.args.get("app_type", "freshdesk")  # default to freshdesk
            endpoint = request.args.get("endpoint")
            params = request.args.get("params", "{}")
            method = request.args.get("method")  # optional GET/POST
            try:
                params = json.loads(params)
            except:
                return jsonify({"status": "error", "message": "params must be a valid JSON string"}), 400

            return fetch_from_freshworks(creds, app_type, endpoint, params, method)

        # Odoo
        elif pt == "odoo":
            model = request.args.get("model")
            method = request.args.get("method")
            args = request.args.get("args", "[]")
            kwargs = request.args.get("kwargs", "{}")
            try:
                args = json.loads(args)
                kwargs = json.loads(kwargs)
            except:
                return jsonify({"status": "error", "message": "args/kwargs must be valid JSON"}), 400

            return fetch_from_odoo(creds, model, method, args, kwargs)

        # ServiceNow
        elif pt == "servicenow":
            endpoint = request.args.get("endpoint")
            params = request.args.get("params", "{}")
            try:
                params = json.loads(params)
            except:
                return jsonify({"status": "error", "message": "params must be a valid JSON string"}), 400

            return fetch_from_servicenow(creds, endpoint, params)

        # SAP
        elif pt == "sap":
            producttype = request.args.get("producttype")
            subproducttype = request.args.get("subproducttype")
            field = request.args.get("field")
            filters = request.args.get("filters")
            return fetch_from_sap(creds, producttype, subproducttype, field, filters)
        
        # HubSpot
        elif pt == "hubspot":
            app_type = request.args.get("app_type", "contacts")
            endpoint = request.args.get("endpoint")
            params = request.args.get("params", "{}")
            try:
                params = json.loads(params)
            except:
                return jsonify({"status": "error", "message": "params must be a valid JSON string"}), 400
            return fetch_from_hubspot(creds, app_type, endpoint, params)
        
        elif pt == "erpnext":
            endpoint = request.args.get("endpoint")
            params = request.args.get("params", "{}")
            method = request.args.get("method", "GET")  # default GET
            try:
                params = json.loads(params)
            except:
                return jsonify({"status": "error", "message": "params must be a valid JSON string"}), 400
            return fetch_from_erpnext(creds, endpoint, params, method)

        else:
            return jsonify({"status": "error", "message": "Unsupported productType"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/metadata/<category>/<product_type>", methods=["GET"])
def get_metadata(category, product_type):
    # Map categories to fetchers
    fetchers = {
        "db": fetch_db_credentials,
        "ss": fetch_ss_credentials,
        "doi": fetch_doi_credentials,
        "ecom": fetch_ecom_credentials,
        "app": fetch_app_credentials
    }

    if category not in fetchers:
        return jsonify({"status": "error", "message": "Invalid category"}), 400

    creds_list = fetchers[category]()
    metadata_map = {c["name"].lower(): c.get("metadata", {}) for c in creds_list}

    if product_type:
        data = metadata_map.get(product_type.lower())
        if not data:
            return jsonify({"status": "error", "message": "Invalid productType"}), 400
        return jsonify({"status": "success", "data": data})

    return jsonify({"status": "success", "data": metadata_map})

if __name__ == "__main__":
    app.run(debug=True)