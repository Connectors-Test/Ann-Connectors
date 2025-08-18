## Guide for using SQLite Credential Manager(this folder)

### Setup

1. Make sure all required files in `\init` has been run once to:
   - Create the SQLite DB (`wwwsmart_credentials.db`)
   - Create required tables: `App_connector_credentials`, `Db_connector_credentials`, ..
   - Load credentials from env for testing

2. What other files do:
   - `modules.py` → This script contains modules for SQLite actions
   - `view_table.py` → This script can be used to view the tables
   - `manager.py` → This script helps manage DB credentials stored via `init.py`
   - `\helper_functions` → This dir contains all other smartcard ingetrator helper modules

### Available Functions (`modules.py`)

| Function           | Description                                      |
|--------------------|--------------------------------------------------|
| `create_table(...)` | Create a new table if needed                    |
| `upsert_credential(...)` | Insert or update credentials              |
| `get_credentials(...)` | Fetch credentials for given user, uuid or product_name |
| `delete_credential(...)` | Delete a specific credential entry        |
| `delete_table(...)` | Drop an entire table (Caution!)                |

### Usage Examples for `manager.py`

```python
from modules import *
from init import PRODUCT_METADATA

DB_NAME = "wwwsmart_credentials.db"
TABLE = "Db_connector_credentials"

# ✅ View stored credentials
creds = get_credentials(DB_NAME, TABLE, "user_001", "uuid_pg", "postgresql")
print(creds)

# ✅ Insert/update credentials
upsert_credential(DB_NAME, TABLE, "user_002", "uuid_pg", "alice", "postgresql", {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "pass",
    "database": "sample_db",
    "query": "SELECT 1"
}, metadata=PRODUCT_METADATA["postgresql"])

# ✅ Delete a credential
delete_credential(DB_NAME, TABLE, "user_001", "uuid_pg", "postgresql")

# ⚠️ Delete entire table
delete_table(DB_NAME, TABLE)