from mssqlConnector import MSSQLConnector

# Start session (it will ask for password)
db = MSSQLConnector(database='SmartCardAI')  # or your DB name

# Print stuff
# print("Databases:", db._fetch_databases())
# print("Tables:", db._fetch_tables())
# print("Columns:", db._fetch_columns())
# print("User Table Data:", db._fetch_data('Users'))
print("Database Fetch:\n",db.fetch_databases())
print("Tables Fetch:\n", db.fetch_tables())
print("Columns Fetch:\n", db.fetch_columns())
print("User Table Data Fetch:\n", db.fetch_data('Users'))

# Done
db.close()