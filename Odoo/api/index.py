from flask import Flask, request, jsonify
import os, json, requests
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load env variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
ODOO_URL = os.getenv("ODOO_URL")
ODOO_KEY = os.getenv("ODOO_KEY")
DB = "smartcardai"
UID = 2

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")


def odoo_rpc(model, method, args=None, kwargs=None):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "id": 1,
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [DB, UID, ODOO_KEY, model, method, args or [], kwargs or {}]
        }
    }
    headers = {"Content-Type": "application/json"}
    r = requests.post(f"{ODOO_URL}/jsonrpc", headers=headers, json=payload)
    return r.json() if r.ok else {"error": r.text}


@app.route("/")
def home():
    return "Odoo-Gemini Flask API Active"


@app.route("/auth")
def auth_check():
    return jsonify({"status": "authenticated"})


@app.route("/get/<model>", methods=["GET"])
def get_model_data(model):
    fields = request.args.get("fields", "id,name").split(",")
    domain = []
    limit = int(request.args.get("limit", 10))
    data = odoo_rpc(model, "search_read", [domain], {"fields": fields, "limit": limit})
    return jsonify(data)


@app.route("/schema/<model>", methods=["GET"])
def get_model_schema(model):
    data = odoo_rpc(model, "fields_get", [], {"attributes": ["string", "type"]})
    return jsonify(data)


@app.route("/listsubtypes/<model>", methods=["GET"])
def list_subtypes(model):
    field = request.args.get("field", "x_studio_subtype")
    data = odoo_rpc(model, "search_read", [], {"fields": [field]})
    unique_vals = sorted(set(d[field] for d in data.get("result", []) if d.get(field)))
    return jsonify({"subtypes": unique_vals})


@app.route("/gemini", methods=["POST"])
def gemini_generate():
    prompt = request.json.get("prompt", "")
    full_prompt = (
        "You are an Odoo API assistant. Take the user's query and convert it into a JSON object.\n"
        "Example:\n"
        "{\n"
        "  'model': 'product.product',\n"
        "  'method': 'search_read',\n"
        "  'args': [[['list_price', '>', 50]]],\n"
        "  'kwargs': { 'fields': ['id', 'name', 'list_price'], 'limit': 5}\n"
        "}\n"
        "Only return raw JSON. Do not include explanations or markdown.\n\n"
        f"User: {prompt}\n\nAPI JSON:"
    )

    try:
        res = model.generate_content(full_prompt).text.strip("`json").strip("`").strip()
        api_call = json.loads(res)

        # Run actual API call
        output = odoo_rpc(
            api_call["model"],
            api_call["method"],
            api_call.get("args", []),
            api_call.get("kwargs", {})
        )
        return jsonify({
            "gemini_response": api_call,
            "odoo_response": output
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
