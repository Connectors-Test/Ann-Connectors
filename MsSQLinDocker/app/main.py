import os
from flask import Flask, request, jsonify
from mssqlConnector import MSSQLConnector  # import your class

app = Flask(__name__)
password = os.environ.get("MsSQLPsswd", "")
db = os.environ.get("MsSQLdb", "")

@app.route("/fetch-databases", methods=["GET"])
def fetch_databases():
    try:
        conn = MSSQLConnector(password=password)
        result = conn.fetch_databases()
        conn.close()
        return jsonify(result)
    except Exception as e:
        print("Error in /fetch-databases:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/fetch-tables", methods=["GET"])
def fetch_tables():
    db = request.args.get("db")
    if not db:
        return jsonify({"error": "Missing database"}), 400

    conn = MSSQLConnector(password=password, database=db)
    result = conn.fetch_tables()
    conn.close()
    return jsonify(result)

@app.route("/fetch-columns", methods=["GET"])
def fetch_columns():
    db = request.args.get("db")
    if not db:
        return jsonify({"error": "Missing database"}), 400

    conn = MSSQLConnector(password=password, database=db)
    result = conn.fetch_columns()
    conn.close()
    return jsonify(result)

@app.route("/fetch-data", methods=["GET"])
def fetch_data():
    db = request.args.get("db")
    table = request.args.get("table")
    if not db or not table:
        return jsonify({"error": "Missing db or table"}), 400

    conn = MSSQLConnector(password=password, database=db)
    result = conn.fetch_data(table)
    conn.close()
    return jsonify(result)

@app.route("/api/data/<dbname>/<tablename>/<columnname>", methods=["GET"])
def get_column_data(dbname, tablename, columnname):
    
    conn = MSSQLConnector(password=password, database=dbname)
    result = conn.fetch_column_data(tablename, columnname)
    conn.close()
    return jsonify(result)

@app.route("/Schema/<tablename>", methods=["GET"])
def get_schema(tablename):
    db = request.args.get("db")
    if not db:
        return jsonify({"error": "Missing database"}), 400

    conn = MSSQLConnector(password=password, database=db)
    result = conn.fetch_table_schema(tablename)
    conn.close()
    return jsonify(result)

@app.route("/listtable/<dbname>", methods=["GET"])
def list_tables(dbname):
    
    conn = MSSQLConnector(password=password, database=dbname)
    result = conn.fetch_tables()
    conn.close()
    return jsonify(result)

@app.route("/listcolumns/<dbname>/<tablename>", methods=["GET"])
def list_columns(dbname, tablename):
    
    conn = MSSQLConnector(password=password, database=dbname)
    result = conn.fetch_column(tablename)
    conn.close()
    return jsonify(result)

@app.route("/Previewdata/<dbname>/<tablename>", methods=["GET"])
def preview_table(dbname, tablename):
    
    conn = MSSQLConnector(password=password, database=dbname)
    result = conn.fetch_preview_data(tablename)
    conn.close()
    return jsonify(result)

@app.route("/query", methods=["GET"])
def run_query():
    db = request.args.get("db")
    query = request.args.get("query")
    table = request.args.get("table")

    if not db or not query:
        return jsonify({"error": "Missing db or query"}), 400

    if table and "FROM" not in query.upper():
        query = f"{query} FROM {table}"
    
    try:
        conn = MSSQLConnector(password=password, database=db)
        result = conn.run_custom_query(query)  # Implement in MSSQLConnector
        conn.close()
        return jsonify(result)
    except Exception as e:
        print("Error in /query:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/metadata", methods=["GET"])
def get_metadata():
    conn = MSSQLConnector(password=password, database=db)
    return jsonify({
        "description": "Microsoft SQL Server connection using pyodbc.",
        "version": f"{conn.fetch_version()}",
        "required_credentials": ["server", "port", "user", "password", "database"],
        "required_parameters": ["db", "table", "query"],
        "query_type": "SQL",
        "example_query": "SELECT TOP 10 *",
        "driver": "ODBC Driver 18 for SQL Server",
        "connection_string_example": (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=server_address,1433;"
            "UID=username;"
            "PWD=password;"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)