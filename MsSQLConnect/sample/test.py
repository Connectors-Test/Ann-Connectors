import pyodbc
from mssqlConnector import (
    DBMSSQLFetchDatabases,
    DBMSSQLFetchTables,
    DBMSSQLFetchColumns,
    DBMSSQLFetchData
)

server = 'localhost'
database = 'SmartCardAI'
username = 'sa'
password = input("Enter your password: ")

conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                      f'SERVER={server};DATABASE={database};'
                      f'UID={username};PWD={password}')
cursor = conn.cursor()
# cursor.execute("SELECT name FROM sys.databases")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

# --- INPUT SETUP ---
userID = username
credentials = {
    "host": server,  # Change if using a remote server
    "password": password
}
databaseName = database
tableName = "Users"  

print("\n=== FETCH DATABASES ===")
print(DBMSSQLFetchDatabases(userID, credentials))

print("\n=== FETCH TABLES ===")
print(DBMSSQLFetchTables(userID, credentials, databaseName))

print("\n=== FETCH COLUMNS ===")
print(DBMSSQLFetchColumns(userID, credentials, databaseName))

print("\n=== FETCH DATA ===")
print(DBMSSQLFetchData(userID, credentials, databaseName, tableName))