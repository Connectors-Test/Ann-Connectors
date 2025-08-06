import requests
import json
import inspect
import os
from dotenv import load_dotenv

load_dotenv()

credentials = { "access_token": os.getenv("AIRTABLE_PAT") }
databaseName = os.getenv("AIRTABLE_BASE_ID")
tableName = os.getenv("AIRTABLE_TABLE_NAME")
queryParams = {
    "maxRecords": 10,
    "pageSize": 5,
    "view": "Grid view",
    "sort[0][field]": "Date",
    "sort[0][direction]": "desc",
    "filterByFormula": "{Deployments} > 0",
    "fields[]": ["Date", "Commits"],
    "cellFormat": "json",
    "timeZone": "Asia/Kolkata",
    "userLocale": "en",
    "returnFieldsByFieldId": "false"
}

def DBAIRTABLEFetchData(credentials, databaseName, tableName, queryParams=None):
    try:
        access_token = credentials.get("access_token")  # Airtable PAT
        url = f"https://api.airtable.com/v0/{databaseName}/{tableName}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        all_records = []
        offset = None

        while True:
            # Flatten Airtable query params (especially fields[] and sort[])
            params = []
            if queryParams:
                for key, value in queryParams.items():
                    if isinstance(value, list):
                        for item in value:
                            params.append((key, item))
                    elif value is not None:
                        params.append((key, value))

            if offset:
                params.append(("offset", offset))

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            records = data.get("records", [])
            all_records.extend(records)

            offset = data.get("offset")
            if not offset:
                break

        formatted_data = []
        for record in all_records:
            fields = record.get("fields", {})
            fields["id"] = record.get("id")
            formatted_data.append(fields)

        return json.dumps(formatted_data, default=str)

    except Exception as e:
        return {
            "success": False,
            "message": "Could not retrieve Airtable data",
            "functionName": inspect.currentframe().f_code.co_name,
            "log": str(e),
            "data": 0,
            "statusCode": 400
        }

print(DBAIRTABLEFetchData(credentials, databaseName, tableName, queryParams))