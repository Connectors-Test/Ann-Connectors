import requests
import json
import inspect
import os
from dotenv import load_dotenv

load_dotenv()

SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", " ")
SHEETS_NAME = os.getenv("GOOGLE_SHEET_NAME", " ")

def fetch_google_sheet_data(sheetsID, sheetName, query):
    try:
        # Build gviz/tq URL for Google Sheets
        base_url = f"https://docs.google.com/spreadsheets/d/{sheetsID}/gviz/tq"
        params = {
            "sheet": sheetName,    # Sheet name
            "tq": query            # Google Visualization Query
        }

        # Send GET request to Google Sheets
        response = requests.get(base_url, params=params)
        
        if response.status_code != 200:
            return {
                "success": False,
                "message": "Failed to fetch data from Google Sheets",
                "statusCode": response.status_code,
                "log": response.text
            }

        # Google returns JS-like response, need to clean it
        text = response.text
        json_text = text[text.find("(")+1:text.rfind(")")]  # Remove function wrapper
        data_json = json.loads(json_text)

        # Extract rows & headers
        headers = [col['label'] for col in data_json['table']['cols']]
        rows = []
        for row in data_json['table']['rows']:
            values = []
            for cell in row['c']:
                values.append(cell['v'] if cell else None)
            rows.append(dict(zip(headers, values)))

        return {
            "success": True,
            "message": "Retrieved spreadsheet data via gviz",
            "data": rows,
            "statusCode": 200
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Could not fetch spreadsheet data",
            "functionName": inspect.currentframe().f_code.co_name,
            "log": str(e),
            "data": 0,
            "statusCode": 400
        }

print(fetch_google_sheet_data(
    SHEETS_ID,
    SHEETS_NAME,
    "SELECT * LIMIT 10"))