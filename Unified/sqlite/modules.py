import sqlite3
import json

def create_table(db_name, table):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            userid TEXT NOT NULL,
            uuid TEXT NOT NULL,
            username TEXT NOT NULL,
            name TEXT NOT NULL,
            credentials TEXT NOT NULL,
            metadata TEXT
        );
    """)
    conn.commit()
    conn.close()

def delete_table(db_name, table):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    conn.close()

def upsert_credential(db_name, table, userid, uuid, username, name, credentials, metadata=None):
    if metadata:
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        required = metadata.get("required_credentials", [])
        missing = [key for key in required if key not in credentials]
        if missing:
            raise ValueError(f"Missing required fields for {name}: {missing}")
        metadata_json = json.dumps(metadata)
    else:
        metadata_json = None

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Check if entry exists
    cursor.execute(f"""
        SELECT COUNT(*) FROM {table}
        WHERE userid=? AND uuid=? AND name=?
    """, (userid, uuid, name))

    exists = cursor.fetchone()[0] > 0
    credentials_json = json.dumps(credentials)

    if exists:
        cursor.execute(f"""
            UPDATE {table}
            SET username=?, credentials=?, metadata=?
            WHERE userid=? AND uuid=? AND name=?
        """, (username, credentials_json, metadata_json, userid, uuid, name))
    else:
        cursor.execute(f"""
            INSERT INTO {table} (userid, uuid, username, name, credentials, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (userid, uuid, username, name, credentials_json, metadata_json))

    conn.commit()
    conn.close()

def get_credentials(db_name, table, userid=None, uuid=None, product_name=None):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    query = f"SELECT userid, uuid, username, name, credentials, metadata FROM {table} WHERE 1=1"
    params = []

    if userid is not None:
        query += " AND userid=?"
        params.append(userid)

    if uuid is not None:
        query += " AND uuid=?"
        params.append(uuid)

    if product_name is not None:
        query += " AND name=?"
        params.append(product_name)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise ValueError(f"No credentials found for given filters: userid={userid}, uuid={uuid}, name={product_name}")

    results = []
    for row in rows:
        try:
            creds = json.loads(row[4])
        except json.JSONDecodeError:
            creds = {"error": "Invalid JSON format"}

        try:
            meta = json.loads(row[5]) if row[5] else {}
        except (IndexError, json.JSONDecodeError):
            meta = {}
        
        results.append({
            "userid": row[0],
            "uuid": row[1],
            "username": row[2],
            "name": row[3],
            "credentials": creds,
            "metadata": meta
        })

    return results

def delete_credential(db_name, table, userid, uuid, name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"""
        DELETE FROM {table}
        WHERE userid=? AND uuid=? AND name=?
    """, (userid, uuid, name))
    conn.commit()
    conn.close()