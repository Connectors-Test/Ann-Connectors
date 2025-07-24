import getpass
import json
import pyodbc
# from sqlalchemy import create_engine
# import pymssql

class MSSQLConnector:
    def __init__(self, server='localhost', user='sa', password=None, database=None):
        self.server = server
        self.user = user
        self.database = database
        self.password = password or getpass.getpass(prompt='Enter MSSQL password: ')
        self.conn = None
        self.cursor = None
        self.connect()

    # def get_engine(username, password, server, database):                                     DRIVERLESS ATTEMPT 1
    #     connection_string = f"mssql+pytds://{username}:{password}@{server}/{database}"
    #     engine = create_engine(connection_string)
    #     return engine

    def connect(self):
        try:
            conn_str = (                                                    #DRIVER METHOD
                f'DRIVER={{ODBC Driver 18 for SQL Server}};'
                f'SERVER={self.server};'
                f'UID={self.user};'
                f'PWD={self.password};'
            )
            if self.database:
                conn_str += f'DATABASE={self.database};'
            self.conn = pyodbc.connect(conn_str)
            self.cursor = self.conn.cursor()
            # # DRIVERLESS ATTEMPT 1
            # connection_string = f"mssql://{self.user}:{self.password}@{self.server}/{self.database or ''}"   
            # self.engine = create_engine(connection_string)
            # self.conn = self.engine.connect()
            # # DRIVERLESS ATTEMPT 2
            # self.conn = pymssql.connect(self.server, self.user, self.password, self.database)
            # self.cursor = self.conn.cursor()
            print(f"[✓] Connected to {self.database or 'server'} as {self.user}")
        except Exception as e:
            print(f"[!] Connection failed: {e}")

    # Fetching method 1 - gives result as lists -  can test using testConnection.py
    def _fetch_databases(self):
        try:
            self.cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4;")
            return [row[0] for row in self.cursor.fetchall()]
            # result = self.conn.execute("SELECT name FROM sys.databases WHERE database_id > 4;")
            # return [row[0] for row in result.fetchall()]
        except Exception as e:
            print(f"[!] Error fetching databases: {e}")
            return []

    def _fetch_tables(self):
        try:
            self.cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
            return [row[0] for row in self.cursor.fetchall()]
            # result = self.conn.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
            # return [row[0] for row in result.fetchall()]
        except Exception as e:
            print(f"[!] Error fetching tables: {e}")
            return []

    def _fetch_columns(self):
        try:
            self.cursor.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS")
            # result = self.conn.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS")
            result = {}
            for row in self.cursor.fetchall():
                table, col = row
                result.setdefault(table, []).append(col)
            return result
        except Exception as e:
            print(f"[!] Error fetching columns: {e}")
            return {}

    def _fetch_data(self, table):
        try:
            self.cursor.execute(f"SELECT * FROM {table}")
            columns = [column[0] for column in self.cursor.description]
            rows = self.cursor.fetchall()
            # result = self.conn.execute(f"SELECT * FROM {table}")
            # columns = [column[0] for column in result.description]
            # rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"[!] Error fetching data from {table}: {e}")
            return []
        
    # Fetching method 2 - gives result as JSON - can be tested using app.py and testConnection.py
    def fetch_databases(self):
        try:
            self.cursor.execute("""
                SELECT name 
                FROM sys.databases 
                WHERE database_id > 4 
                  AND state = 0 
                  AND name NOT IN ('distribution')
                ORDER BY name
            """)
            dbs = [row[0] for row in self.cursor.fetchall()]
            return {
                "success": True,
                "message": "Retrieved MSSQL database names",
                "data": dbs,
                "statusCode": 200
            }
        except Exception as e:
            return self._error_response("fetch_databases", e)

    def fetch_tables(self):
        try:
            self.cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            tables = [row[0] for row in self.cursor.fetchall()]
            return {
                "success": True,
                "message": "retrieved mssql table names",
                "data": tables,
                "statusCode": 200
            }
        except Exception as e:
            return self._error_response("fetch_tables", e)

    def fetch_columns(self):
        try:
            self.cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            tables = [row[0] for row in self.cursor.fetchall()]

            columns_dict = {}
            for table in tables:
                self.cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", table)
                columns = [col[0] for col in self.cursor.fetchall()]
                columns_dict[table] = columns

            return {
                "success": True,
                "message": "retrieved mssql column names",
                "data": columns_dict,
                "statusCode": 200
            }
        except Exception as e:
            return self._error_response("fetch_columns", e)

    def fetch_data(self, tableName):
        try:
            self.cursor.execute(f"SELECT * FROM {tableName}")
            columns = [col[0] for col in self.cursor.description]
            rows = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            return {
                "success": True,
                "message": "retrieved mssql data",
                "data": json.dumps(rows, default=str),
                "statusCode": 200
            }
        except Exception as e:
            return self._error_response("fetch_data", e)

    def _error_response(self, func_name, exception):
        return {
            "success": False,
            "message": f"could not perform {func_name}",
            "functionName": func_name,
            "log": str(exception),
            "data": 0,
            "statusCode": 400
        }

    def fetch_column_data(self, table, column):
        query = f"SELECT DISTINCT [{column}] FROM [{table}]"
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]
    
    def fetch_column(self, table):
        query = f"""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ?
        """
        self.cursor.execute(query, (table,))
        columns = [row[0] for row in self.cursor.fetchall()]
        return {"columns": columns}
    
    def fetch_table_schema(self, table):
        query = f"""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table}'
        """
        self.cursor.execute(query)
        return [dict(zip(['column_name', 'data_type', 'is_nullable'], row)) for row in self.cursor.fetchall()]

    def fetch_preview_data(self, table, limit=5):
        query = f"SELECT TOP {limit} * FROM [{table}]"
        self.cursor.execute(query)
        columns = [col[0] for col in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("[✓] Connection closed.")