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

es.indices.put_mapping(
    index="intern-test",
    body={
        "properties": {
            "name_suggest": {"type": "completion"}
        }
    }
)

# Create some test documents
docs = [
    {"name": "John Doe", "name_suggest": "John Doe", "email": "john@example.com", "skills": ["python", "flask"], "experience": 2},
    {"name": "Jane Smith", "name_suggest": "Jone Smith", "email": "jane@example.com", "skills": ["react", "node"], "experience": 3},
    {"name": "Bob Alex", "name_suggest": "Bob Alex", "email": "bob@example.com", "skills": ["java", "spring"], "experience": 1},
]

for i, doc in enumerate(docs):
    es.index(index="intern-test", id=i+1, document=doc)

@app.route("/search", methods=["GET"])
def search_all():
    """
    Query everything in Elasticsearch.
    Supports:
    - index (optional): specific index to query
    - q: search query (defaults to match_all)
    - size: number of results (default 10)
    """
    index = request.args.get("index", "*")  # Search all indices by default
    query_text = request.args.get("q", None)
    size = int(request.args.get("size", 10))

    if query_text:
        query = {
            "query": {
                "query_string": {
                    "query": query_text
                }
            }
        }
    else:
        query = {"query": {"match_all": {}}}

    try:
        response = es.search(index=index, query=query["query"], size=size)
        return jsonify(response.body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/indices", methods=["GET"])
def list_indices():
    """List all indices in the Elasticsearch cluster."""
    try:
        indices = es.cat.indices(format="json")
        index_names = [i["index"] for i in indices]
        return jsonify(index_names)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/doc/<index>/<doc_id>", methods=["GET"])
def get_document(index, doc_id):
    """Fetch a specific document by index and ID."""
    try:
        doc = es.get(index=index, id=doc_id)
        return jsonify(doc.body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/<index>/mapping", methods=["GET"])
def get_index_mapping(index):
    """Returns mapping (schema) of a given index."""
    try:
        mapping = es.indices.get_mapping(index=index)
        return jsonify(mapping.get(index, {}))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/<index>/fields", methods=["GET"])
def get_index_fields(index):
    """Lists all fields in a given index."""
    try:
        mapping = es.indices.get_mapping(index=index)
        props = mapping.get(index, {}).get("mappings", {}).get("properties", {})
        fields = list(props.keys())
        return jsonify(fields)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/<index>/count", methods=["POST"])
def count_documents(index):
    """Counts documents in the index matching a query."""
    try:
        query = request.get_json(force=True)
        count = es.count(index=index, query=query.get("query", {"match_all": {}}))
        return jsonify(count.body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/suggest/<index>", methods=["POST"])
def suggest_query(index):
    """Suggest/autocomplete using suggest API on a specific index."""
    try:
        body = request.get_json(force=True)
        response = es.search(index=index, body=body)
        return jsonify(response.body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/<index>/aggregations", methods=["POST"])
def aggregation_query(index):
    """Performs an aggregation query on the index."""
    try:
        body = request.get_json(force=True)
        result = es.search(index=index, body=body)
        return jsonify(result.body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/search-multi", methods=["POST"])
def multi_index_search():
    """Search multiple indices and fields."""
    try:
        body = request.get_json(force=True)
        indices = body.get("indices", "*")
        query = body.get("query", {"match_all": {}})
        response = es.search(index=indices, query=query)
        return jsonify(response.body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
