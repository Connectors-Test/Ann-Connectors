import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069/jsonrpc")
DB = os.getenv("ODOO_DB", "SCAI")
USER = os.getenv("ODOO_EMAIL", "")
PASSWORD = os.getenv("ODOO_PASS", "")
HEADERS = {"Content-Type": "application/json"}

def call(method, params):
    payload = {
    "jsonrpc": "2.0",
    "method": method,
    "params": params,
    "id": 1
    }
    res = requests.post(ODOO_URL, data=json.dumps(payload), headers=HEADERS)
    res.raise_for_status()
    result = res.json()

    if "error" in result:
        raise Exception(f"Odoo RPC Error: {result['error']}")
    if "result" not in result:
        raise Exception(f"Unexpected response: {result}")

    return result["result"]

def login():
    return call("call", {
    "service": "common",
    "method": "login",
    "args": [DB, USER, PASSWORD]
    })

UID = login()

def create(model, data):
    return call("call", {
    "service": "object",
    "method": "execute_kw",
    "args": [DB, UID, PASSWORD, model, "create", [data]]
    })

def read(model, ids, fields=None):
    return call("call", {
    "service": "object",
    "method": "execute_kw",
    "args": [DB, UID, PASSWORD, model, "read", [ids], {"fields": fields or []}]
    })

def search(model, domain=None):
    return call("call", {
    "service": "object",
    "method": "execute_kw",
    "args": [DB, UID, PASSWORD, model, "search", [domain or []]]
    })

def search_read(model, domain=None, fields=None):
    return call("call", {
    "service": "object",
    "method": "execute_kw",
    "args": [DB, UID, PASSWORD, model, "search_read", [domain or []], {"fields": fields or []}]
    })

def update(model, ids, values):
    return call("call", {
    "service": "object",
    "method": "execute_kw",
    "args": [DB, UID, PASSWORD, model, "write", [ids, values]]
    })

def delete(model, ids):
    return call("call", {
    "service": "object",
    "method": "execute_kw",
    "args": [DB, UID, PASSWORD, model, "unlink", [ids]]
    })