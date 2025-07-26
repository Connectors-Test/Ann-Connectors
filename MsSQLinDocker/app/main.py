import os
from flask import Flask, request, jsonify
from app.mssqlConnector import MSSQLConnector  # import your class

app = Flask(__name__)
password = os.environ.get("MsSQLPsswd", "")

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)