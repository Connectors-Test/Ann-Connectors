import requests
import json
import urllib.parse

def fetch_from_googlesheet(creds, query):
    """
    Fetch data from a Google Sheet published via the gviz API.
    creds: dict containing at least {'sheet_id': 'https://.../gviz/tq?tq='}
    query: SQL-like query string (e.g., "SELECT *")
    """
    if not query.strip().lower().startswith("select"):
        return {"status": "error", "message": "Only SELECT queries are allowed"}

    forbidden = ["update", "delete", "insert", "drop", "alter"]
    if any(word in query.lower() for word in forbidden):
        return {"status": "error", "message": "Forbidden operation in query"}

    try:
        # Construct full URL
        base_url = f"https://docs.google.com/spreadsheets/d/{creds['sheet_id']}/gviz/tq?tq="
        encoded_query = urllib.parse.quote(query) # URL-encode the query string
        url = base_url + encoded_query

        response = requests.get(url)
        response.raise_for_status()

        # Google Sheets "gviz" API wraps JSON inside JS function call
        text = response.text
        json_start = text.find("({") + 1
        json_end = text.rfind("})") + 1
        raw_json = text[json_start:json_end]

        data = json.loads(raw_json)

        # Optional: normalize the data into list of dicts
        table = data.get("table", {})
        cols = [c.get("label", f"col_{i}") for i, c in enumerate(table.get("cols", []))]
        rows = [
            {cols[i]: (cell.get("v") if cell else None) for i, cell in enumerate(r.get("c", []))}
            for r in table.get("rows", [])
        ]

        return rows

    except Exception as e:
        return {"status": "error", "message": f"Google Sheet fetch failed: {str(e)}"}