from flask import Flask, jsonify, request
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

@app.route('/contacts', methods=['GET'])
def list_contacts():
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts"
    r = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS)
    return jsonify(r.json()), r.status_code

@app.route('/create-ticket', methods=['POST'])
def create_ticket():
    data = {
        "description": "Test ticket from API",
        "subject": "API Test",
        "email": "demo.user@example.com",
        "priority": 1,
        "status": 2
    }
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets"
    r = requests.post(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS, json=data)
    return jsonify(r.json()), r.status_code

@app.route('/add-note/<int:ticket_id>', methods=['POST'])
def add_note(ticket_id):
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}/notes"
    data = {"body": "This is a note added via API", "private": True}
    r = requests.post(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS, json=data)
    return jsonify(r.json()), r.status_code

@app.route('/archived-ticket/<int:ticket_id>', methods=['GET'])
def archived_ticket(ticket_id):
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/archived/{ticket_id}"
    r = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS)
    return jsonify(r.json()), r.status_code

@app.route('/schema/<endpoint>', methods=['GET'])
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

@app.route('/list-subtypes/<endpoint>', methods=['GET'])
def list_subtypes(endpoint):
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/{endpoint}"
    try:
        response = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            indices = list(range(len(data)))
            return jsonify({"indices": indices}), 200
        else:
            return jsonify({"indices": []}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
