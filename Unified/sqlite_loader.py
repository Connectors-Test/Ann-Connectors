from sqlite.modules import get_credentials
DB_PATH = "./wwwsmart_credentials.db"

def fetch_api_credentials(user_id=None):
    return get_credentials(DB_PATH, "Api_connector_credentials", userid=user_id)

def fetch_db_credentials(user_id=None):
    return get_credentials(DB_PATH, "Db_connector_credentials", userid=user_id)
