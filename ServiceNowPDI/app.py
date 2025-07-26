from flask import Flask, jsonify, render_template
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Replace these with your own
SERVICENOW_INSTANCE = os.getenv("SERVICENOW_INSTANCE")
USERNAME = os.getenv("SERVICENOW_USER")
PASSWORD = os.getenv("SERVICENOW_PASS")

HEADERS = {"Accept": "application/json"}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/users")
def get_users():
    url = f"{SERVICENOW_INSTANCE}/api/now/table/sys_user"
    res = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    return jsonify(res.json())

@app.route("/api/incidents")
def get_incidents():
    url = f"{SERVICENOW_INSTANCE}/api/now/table/incident"
    res = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    return jsonify(res.json())

@app.route("/api/user_count")
def get_user_count():
    url = f"{SERVICENOW_INSTANCE}/api/now/stats/sys_user?sysparm_count=true"
    res = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    return jsonify(res.json())

if __name__ == "__main__":
    app.run(debug=True)
