from flask import Flask, jsonify
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

FRESHDESK_DOMAIN = os.getenv("FRESHDESK_DOMAIN", "")
API_KEY = os.getenv("API_KEY", "")
HEADERS = {"Content-Type": "application/json"}

@app.route('/')
def home():
    return jsonify({"message": "Freshdesk API Flask on Vercel!"})

# ✅ Auth test
@app.route('/auth', methods=['GET'])
def test_auth():
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/agents/me"
    try:
        r = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        return jsonify({"status": "success", "name": data.get("contact", {}).get("name")}), 200
    except Exception as e:
        return jsonify({"status": "fail", "error": str(e)}), 401

# ✅ Basic GET endpoints
@app.route('/contacts', methods=['GET'])
def get_contacts():
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts"
    r = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS)
    return jsonify(r.json()), r.status_code

@app.route('/tickets', methods=['GET'])
def get_tickets():
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets"
    r = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS)
    return jsonify(r.json()), r.status_code

@app.route('/ticket/<int:ticket_id>', methods=['GET'])
def get_single_ticket(ticket_id):
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}"
    r = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS)
    return jsonify(r.json()), r.status_code

@app.route('/agents', methods=['GET'])
def get_agents():
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/agents"
    r = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS)
    return jsonify(r.json()), r.status_code

@app.route('/groups', methods=['GET'])
def get_groups():
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/groups"
    r = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS)
    return jsonify(r.json()), r.status_code

@app.route('/companies', methods=['GET'])
def get_companies():
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/companies"
    r = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS)
    return jsonify(r.json()), r.status_code

# ✅ Schema guesser
@app.route('/schema/<path:endpoint>', methods=['GET'])
def get_schema(endpoint):
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/{endpoint}"
    r = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS)
    if r.status_code != 200:
        return jsonify({"error": r.text}), r.status_code

    data = r.json()
    schema = {}
    if isinstance(data, list) and data:
        for key, value in data[0].items():
            schema[key] = type(value).__name__
    elif isinstance(data, dict):
        for key, value in data.items():
            schema[key] = type(value).__name__
    else:
        return jsonify({"warning": "Unrecognized data format"}), 200

    return jsonify(schema), 200

# ✅ List subtypes (index generator)
@app.route('/list-subtypes/<path:endpoint>', methods=['GET'])
def list_subtypes(endpoint):
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/{endpoint}"
    try:
        r = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            return jsonify({"indices": list(range(len(data)))}), 200
        else:
            return jsonify({"indices": []}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
