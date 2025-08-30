import sqlite3
import json

def view_table_json(db_name, table):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    print(f"\n Table: {table}")

    cursor.execute(f"PRAGMA table_info({table});")
    columns = [col[1] for col in cursor.fetchall()]

    cursor.execute(f"SELECT * FROM {table};")
    rows = cursor.fetchall()

    for row in rows:
        record = dict(zip(columns, row))
        print("\n📄 Record:")
        for key, value in record.items():
            if key in ["credentials", "metadata"]:
                try:
                    parsed = json.loads(value)
                    print(f"🔸 {key}:\n{json.dumps(parsed, indent=2)}")
                except:
                    print(f"🔸 {key}: {value}")
            else:
                print(f"🔹 {key}: {value}")
    conn.close()

view_table_json("wwwsmart_credentials.db", "DoI_connector_credentials")
# view_table_json("wwwsmart_credentials.db", "SS_connector_credentials")