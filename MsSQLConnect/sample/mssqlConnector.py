import pyodbc
import inspect
import json

def DBMSSQLFetchTables(userID, credentials, databaseName):
    try:
        userID = userID.split('-separator-')[0]
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={credentials.get('host')};"
            f"DATABASE={databaseName};"
            f"UID={userID};"
            f"PWD={credentials.get('password')}"
        )
        sqlClient = pyodbc.connect(conn_str)
        sqlCursor = sqlClient.cursor()

        sqlCursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tableNameList = [row[0] for row in sqlCursor.fetchall()]

        return {
            "success": True,
            "message": "retrieved mssql table names",
            "data": tableNameList,
            "statusCode": 200
        }

    except Exception as e:
        return {
            "success": False,
            "message": "could not retrieve mssql table names",
            "functionName": inspect.currentframe().f_code.co_name,
            "data": 0,
            "log": str(e),
            "statusCode": 400
        }
    finally:
        sqlCursor.close()
        sqlClient.close()

def DBMSSQLFetchColumns(userID, credentials, databaseName):
    try:
        userID = userID.split('-separator-')[0]
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={credentials.get('host')};"
            f"DATABASE={databaseName};"
            f"UID={userID};"
            f"PWD={credentials.get('password')}"
        )
        sqlClient = pyodbc.connect(conn_str)
        sqlCursor = sqlClient.cursor()

        sqlCursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tableNameList = [row[0] for row in sqlCursor.fetchall()]

        columnsDict = {}
        for table in tableNameList:
            sqlCursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", table)
            columns = [col[0] for col in sqlCursor.fetchall()]
            columnsDict[table] = columns

        return {
            "success": True,
            "message": "retrieved mssql column names",
            "data": columnsDict,
            "statusCode": 200
        }

    except Exception as e:
        return {
            "success": False,
            "message": "could not retrieve mssql column names",
            "functionName": inspect.currentframe().f_code.co_name,
            "log": str(e),
            "data": 0,
            "statusCode": 400
        }
    finally:
        sqlCursor.close()
        sqlClient.close()

def DBMSSQLFetchData(userID, credentials, databaseName, tableName):
    try:
        userID = userID.split('-separator-')[0]
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={credentials.get('host')};"
            f"DATABASE={databaseName};"
            f"UID={userID};"
            f"PWD={credentials.get('password')}"
        )
        sqlClient = pyodbc.connect(conn_str)
        sqlClient.setencoding(encoding='utf-8')
        sqlCursor = sqlClient.cursor()
        sqlCursor.execute(f"SELECT * FROM [ONEX].{tableName}")

        columns = [column[0] for column in sqlCursor.description]
        rows = [dict(zip(columns, row)) for row in sqlCursor.fetchall()]

        return {
            "success": True,
            "message": "retrieved mssql data",
            "data": json.dumps(rows, default=str),
            "statusCode": 200
        }

    except Exception as e:
        return {
            "success": False,
            "message": "could not retrieve mssql data",
            "functionName": inspect.currentframe().f_code.co_name,
            "log": str(e),
            "data": 0,
            "statusCode": 400
        }
    finally:
        sqlCursor.close()
        sqlClient.close()

def DBMSSQLFetchDatabases(userID, credentials):
    try:
        userID = userID.split('-separator-')[0]         # Split the string to get the user ID
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={credentials.get('host')};"
            f"UID={userID};"
            f"PWD={credentials.get('password')};"
            "DATABASE=master"  # Connect to master database to list all databases
        )
        sqlClient = pyodbc.connect(conn_str)
        sqlCursor = sqlClient.cursor()

        # Query to get user databases, excluding system databases
        sqlCursor.execute("""
            SELECT name 
            FROM sys.databases 
            WHERE database_id > 4  -- Excludes system databases (master, tempdb, model, msdb)
            AND state = 0  -- Only online databases
            AND name NOT IN ('distribution')  -- Exclude replication database if exists
            ORDER BY name;
        """)
        
        dbNameList = [row[0] for row in sqlCursor.fetchall()]

        return {
            "success": True,
            "message": "Retrieved MSSQL database names",
            "data": dbNameList,
            "statusCode": 200
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Could not retrieve MSSQL database names",
            "functionName": inspect.currentframe().f_code.co_name,
            "log": str(e),
            "data": 0,
            "statusCode": 400
        }
    finally:
        if 'sqlCursor' in locals():
            sqlCursor.close()
        if 'sqlClient' in locals():
            sqlClient.close()
