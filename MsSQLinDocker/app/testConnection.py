from MsSQLinDocker.app.mssqlConnector import MSSQLConnector

db = MSSQLConnector()  # or your DB name

print("Database Fetch:\n",db.fetch_databases())
print("Tables Fetch:\n", db.fetch_tables())
print("Columns Fetch:\n", db.fetch_columns())
print("User Table Data Fetch:\n", db.fetch_data('Users'))

db.close()