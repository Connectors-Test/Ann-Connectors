from flask import Flask, request, jsonify
import databricks.sql
import json
import inspect
import re
import os
from dotenv import load_dotenv

load_dotenv()

credentials = {
"server_hostname": os.getenv("DATABRICKS_SERVER_HOSTNAME"),
"http_path": os.getenv("DATABRICKS_HTTP_PATH"),
"access_token": os.getenv("DATABRICKS_ACCESS_TOKEN")
}

app = Flask(__name__)

def is_safe_select(query):
    """
    Validate that the query is a SELECT statement and does not contain
    destructive keywords like UPDATE, DELETE, INSERT, DROP, etc.
    """
    if not query:
        return False
    # Remove leading/trailing spaces and convert to lowercase
    q = query.strip().lower()
    # Must start with SELECT
    if not q.startswith("select"):
        return False
    # Disallow any dangerous keywords
    dangerous = ["update", "delete", "insert", "drop", "alter", "truncate"]
    return not any(word in q for word in dangerous)

def DBDatabricksFetchData(credentials, databaseName=None, tableName=None, query=None):
    conn = None
    cursor = None
    try:
        # Connect to Databricks
        conn = databricks.sql.connect(
            server_hostname=credentials.get("server_hostname"),
            http_path=credentials.get("http_path"),
            access_token=credentials.get("access_token")
        )
        cursor = conn.cursor()

        # Validate and set SQL query
        if query:
            if not is_safe_select(query):
                raise ValueError("Only SELECT statements are allowed.")
            sql_query = query
        else:
            sql_query = f"SELECT * FROM {databaseName}.{tableName}"

        # Execute query
        cursor.execute(sql_query)

        # Get column names
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        # Convert to list of dictionaries
        results = [dict(zip(columns, row)) for row in rows]

        return results
    
    except Exception as e:
        return {
            "success": False,
            "message": "Could not retrieve Databricks data",
            "functionName": inspect.currentframe().f_code.co_name,
            "log": str(e),
            "data": [],
            "statusCode": 400
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/databricks/fetch', methods=['POST'])
def fetch_databricks_data():
    data = request.json
    credentials = data.get("credentials")
    databaseName = data.get("databaseName")
    tableName = data.get("tableName")
    query = data.get("query")  # Optional

    result = DBDatabricksFetchData(credentials, databaseName, tableName, query)
    return jsonify(result)

# if __name__ == '__main__':
#     app.run(debug=True)

print(
    DBDatabricksFetchData(credentials, databaseName="default", tableName="DevOps", query="SELECT * FROM DevOps LIMIT 10")
)