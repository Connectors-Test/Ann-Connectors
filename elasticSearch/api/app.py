from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

# ---- Elastic Cloud Connection ----
ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID", "")
ELASTIC_USERNAME = os.getenv("ELASTIC_USERNAME", "")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "")

# Initialize Elasticsearch client
es = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID,
    basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
)

@app.route("/", methods=["GET"])
def elastic_home():
    return jsonify({
        "status": "Elastic API is active",
        "endpoints": [
            "/Api/data/Elastic/<Dbname>/ListofTables",
            "/Api/data/Elastic/<Dbname>/<Tablename>/ListofColumns",
            "/Api/data/Elastic/<Dbname>/<Tablename>/Schema",
            "/Api/data/Elastic/<Dbname>/<Tablename>",
            "/Api/data/Elastic/Auth",
        ]
    })

@app.route("/Api/data/Elastic/Auth", methods=["GET"])
def elastic_auth():
    try:
        health = es.cluster.health()
        return jsonify({"status": "connected", "cluster_status": health["status"]})
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

@app.route("/Api/data/Elastic/<dbname>/ListofTables", methods=["GET"])
def list_tables(dbname):
    try:
        indices = es.cat.indices(format="json")
        index_names = [i["index"] for i in indices]
        return jsonify(index_names)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/Api/data/Elastic/<dbname>/<tablename>/ListofColumns", methods=["GET"])
def list_columns(dbname, tablename):
    try:
        mapping = es.indices.get_mapping(index=tablename)
        props = mapping.get(tablename, {}).get("mappings", {}).get("properties", {})
        return jsonify(list(props.keys()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/Api/data/Elastic/<dbname>/<tablename>/Schema", methods=["GET"])
def get_schema(dbname, tablename):
    try:
        mapping = es.indices.get_mapping(index=tablename)
        return jsonify(mapping.get(tablename, {}))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/Api/data/Elastic/<dbname>/<tablename>", methods=["GET"])
def get_sample_data(dbname, tablename):
    try:
        response = es.search(index=tablename, query={"match_all": {}}, size=10)
        return jsonify(response.body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
application = app