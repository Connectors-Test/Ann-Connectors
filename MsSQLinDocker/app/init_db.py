import time
import pyodbc
import os

server = os.getenv("MsSQLserver", "localhost")
user = os.getenv("MsSQLuser", "sa")
password = os.getenv("MsSQLpassword", "")
database = "master"  # start with master, we'll create SCAI

init_sql_path = "/app/init.sql"  # make sure you copy this in Dockerfile

# Connection string
conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};UID={user};PWD={password};TrustServerCertificate=yes"

def wait_for_db(timeout=60):
    for _ in range(timeout):
        try:
            conn = pyodbc.connect(conn_str, timeout=5)
            conn.close()
            print("[+] SQL Server is ready.")
            return True
        except Exception as e:
            print("[...] Waiting for SQL Server:", e)
            time.sleep(1)
    return False

def run_init_sql():
    print("[+] Running init.sql...")
    with open(init_sql_path, "r") as file:
        sql_script = file.read()

    with pyodbc.connect(conn_str, autocommit=True) as conn:
        cursor = conn.cursor()
        for stmt in sql_script.split("GO"):
            stmt = stmt.strip()
            if stmt:
                cursor.execute(stmt)
        print("[+] init.sql executed successfully.")

if __name__ == "__main__":
    if wait_for_db():
        run_init_sql()
    else:
        print("[!] SQL Server did not become ready in time.")
