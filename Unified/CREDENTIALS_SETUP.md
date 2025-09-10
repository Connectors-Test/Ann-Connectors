# Credentials Setup Guide

This guide provides detailed steps to obtain and configure credentials for all supported connectors. Copy values into your `.env` file according to `.env.example`.

---

## Application Connectors (App)

### Freshworks (Freshdesk)

1. Log in to your Freshdesk account.
2. Go to **Profile Settings → API Key**.
3. Copy the API Key.
4. Your domain is the Freshdesk URL (e.g., `company.freshdesk.com`).

---

### Zoho

1. Visit [Zoho API Console](https://api-console.zoho.com/).
2. Create a **Self-Client** app.
3. Copy **Client ID** and **Client Secret**.
4. Generate a **Refresh Token** using Zoho's Generate code.
5. Get your **Organization ID** from Zoho Books/CRM account.

---

### Odoo

1. Log into your Odoo instance.
2. Create a new API key from **My Profile → Account Security**.
3. Note your database name and UID.

---

### ServiceNow

1. Go to [ServiceNow Developer Portal](https://developer.servicenow.com/).
2. Register for a dev instance.
3. Use your instance URL, username, and password.

---

### SAP Sandbox

1. Sign up for [SAP API Hub](https://api.sap.com/).
2. Get the Sandbox API Key.

---

### HubSpot

1. Log into [HubSpot Developer Portal](https://developers.hubspot.com/).
2. Create an app and generate access tokens.

---

### ERPNext

1. Go to [frappecloud.com](https://frappecloud.com?utm_source=chatgpt.com)
2. Start a site using free trial, add that site url to the .env base_url
3. Go to https://your-base-url/app/users -> User -> Select you user
4. From there go to Roles & Permissions -> Select All -> Save
5. Then move to the Setting tab -> API Access -> Generate Keys, add that key and secret seperately to the .env

---

## Database Connectors (DB)

### Databricks
1. Log into your Databricks workspace.
2. Go to **User Settings → Access Tokens**, create a token.
3. Copy your **Workspace URL (hostname)** and **SQL Warehouse ID** from the SQL Warehouses page.

---

### PostgreSQL
1. If hosted locally: use `localhost` as host, port is usually `5432`.
2. If hosted on a server (e.g. AWS RDS, Azure, GCP):  
   - Find **Host/Endpoint** in the DB instance details.  
   - Default **Port** = `5432`.  
   - Use the **username** and **password** you created during setup.  
   - **Database name** is the one you created inside the server.  

---

### MySQL
1. If hosted locally: use `localhost` as host, port is usually `3306`.  
2. If hosted on a provider (e.g. AWS RDS, Azure, GCP):  
   - Find **Host/Endpoint** in the DB instance details.  
   - Default **Port** = `3306`.  
   - Use the **username** and **password** you created during setup.  
   - **Database name** is the one you created in MySQL.  

---

### TimescaleDB
1. TimescaleDB runs on PostgreSQL, so connection details are the same as PostgreSQL.  
2. If using [Timescale Cloud](https://console.cloud.timescale.com/):  
   - Go to your service dashboard.  
   - Copy **Host**, **Port** (default `5432`), **Username**, and **Password**.  
   - **Database name** will usually be `tsdb` unless renamed.  
   - Note: You may also see `sslmode=require` in the connection string, use that if provided.  

---

### Supabase
1. Log in to [Supabase](https://supabase.com/).  
2. Go to **Project Settings → Database** to get Host, Port, User, Password, Database.  
3. Alternatively, copy the **connection string** directly from the settings page.  

---

### MongoDB
1. Use [MongoDB Atlas](https://cloud.mongodb.com/).  
2. Create a cluster.  
3. Go to **Database → Connect → Drivers**, copy the connection URI.  
4. Replace `<username>` and `<password>` with the database user credentials you create.  

---

### Snowflake
1. Log into Snowflake.  
2. Collect these:  
   - **Account identifier** (from URL or admin panel).  
   - **Username / Password** (from user setup).  
   - **Warehouse name** (SQL warehouse you will query).  
   - **Database** and **Schema** (defined in your project).  

---

### Airtable
1. Log into [Airtable](https://airtable.com/).  
2. Get API Key from **Account Settings**.  
3. Get **Base ID** and **Table Name** from the [Airtable API docs](https://airtable.com/api).  

---

### Neo4j
1. Log into [Neo4j Aura](https://neo4j.com/cloud/aura/) or your self-hosted instance.  
2. Get:  
   - **Bolt URI** (e.g. `neo4j+s://<random-id>.databases.neo4j.io`).  
   - **Username** (default `neo4j` unless changed).  
   - **Password** (set when database was created).  

---

### Oracle 
1. Download your required version of Oracle dB from their [official site](https://www.oracle.com/database/technologies/oracle-database-software-downloads.html)
2. Note the service name (something like ORCLPDB1 by default) you give while creating db during installation
3. After successful installation run `sqlplus sys/<your_password>@localhost:1521/<your_service_name> as sysdba`
4. Create new user inside sqlplus using
```bash
CREATE USER <user_name> IDENTIFIED BY <user_password>;
GRANT CONNECT, RESOURCE TO <user_name>;
ALTER USER <user_name> QUOTA UNLIMITED ON users;
EXIT
```
5. Create your required tables from that user after running `sqlplus <user_name>/<user_password>@localhost:1521/<your_service_name> as sysdba`
6. Use these credentials in your .env

## DevOps & IoT Connectors (DOI)

### ClickHouse
1. If hosted locally: use `http://localhost:8123` (HTTP) or `tcp://localhost:9000` (native).
2. For managed ClickHouse (e.g., ClickHouse Cloud, Altinity, Aiven):
   - Find your **Base URL** in the service dashboard.
   - Provide **Username** and **Password** you created.
   - Select the **Database** (usually `default` unless changed).

---

### Tempo (Grafana Tempo)
1. Log in to your [Grafana Cloud](https://grafana.com/) account.
2. Navigate to **Your Stack → Tempo**.
3. Collect:
   - **Base URL** (e.g., `https://tempo-<region>.grafana.net/tempo`).
   - **Username** = Grafana Service Account ID.
   - **API Token** = Generated from Grafana Service Account.

---

### Loki (Grafana Loki)
1. Log in to your [Grafana Cloud](https://grafana.com/) account.
2. Navigate to **Your Stack → Loki**.
3. Collect:
   - **Base URL** (e.g., `https://<stack-id>.grafana.net`).
   - **Username** = Grafana Service Account ID.
   - **API Token** = Generated from Grafana Service Account.
4. Notes:
   - API queries run via `/loki/api/v1/query_range`.
   - Logs may require a lookback window (`minutes`) to ensure results.

---

### Prometheus
1. Log in to your [Grafana Cloud](https://grafana.com/) account.
2. Navigate to **Your Stack → Prometheus**.
3. Collect:
   - **Base URL** (e.g., `https://prometheus-<region>.grafana.net/api/prom`).
   - **Username** = Grafana Service Account ID.
   - **API Token** = Generated from Grafana Service Account.

---

### InfluxDB (2.x)
1. If self-hosted:
   - Default URL: `http://localhost:8086`.
   - Create a new **Organization**, **Bucket**, and **API Token** via the InfluxDB UI.
2. If using [InfluxDB Cloud](https://cloud2.influxdata.com/):
   - Go to **Load Data → Buckets** to find your bucket name.
   - Generate a **Token** under **Data → API Tokens**.
   - Find your **Org** name in account settings.
3. Collect:
   - **url** = InfluxDB API endpoint.
   - **token** = API token you created.
   - **org** = Organization name.
   - **bucket** = Target bucket.

---

### TimescaleDB
1. TimescaleDB is PostgreSQL with time-series extensions.
2. If using [Timescale Cloud](https://console.cloud.timescale.com/):
   - Copy **Host**, **Port** (usually `5432`), **Username**, and **Password**.
   - Database name usually `tsdb` unless renamed.
   - Note: Some setups require `sslmode=require`.
3. If self-hosted, follow PostgreSQL setup.

---

### Redis
1. If self-hosted locally:
   - Default Host = `localhost`, Port = `6379`.
   - No username/password required unless configured.
2. If using [Redis Cloud](https://redis.com/redis-enterprise-cloud/):
   - Copy **Host**, **Port**, **Username**, and **Password** from your instance dashboard.
   - Ensure correct TLS/SSL settings if required.
3. Example:
   - Command = `LRANGE`
   - Args = `logs,0,10`

---

### Elasticsearch
1. If using [Elastic Cloud](https://cloud.elastic.co/):
   - Find your **Cloud ID** in the deployment dashboard.
   - Create a new user or API key for auth.
   - Collect **Username** and **Password** (or API key).
2. If self-hosted:
   - Use your server endpoint and port (`http://localhost:9200`).
   - Default username = `elastic`, password set during setup.
3. Notes:
   - `index` must exist (e.g., `logs-*`).
   - Queries use **Elasticsearch DSL** JSON format.

---

### OpenSearch (Docker)
1. Make sure Docker is installed
2. Pull the OpenSearch image: `docker pull opensearchproject/opensearch:latest` (run in cmd)
3. Run container: Change your password and run the below command
```bash
docker run -d -p 9200:9200 -p 9600:9600 -e "discovery.type=single-node" -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=Your password" -e "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m" opensearchproject/opensearch:latest
```

---

## E-Commerce Connectors (ECOM)

### Zoho
1. Log into [Zoho](https://www.zoho.com/) and navigate to your **Zoho API Console**.  
2. Create a **self-client** and generate a **Refresh Token** using your client credentials.  
   - Docs: [Zoho OAuth Tokens](https://www.zoho.com/accounts/protocol/oauth.html).  
3. Collect the following:  
   - **Refresh Token** (OAuth refresh token for API calls).  
   - **Client ID** and **Client Secret** (from API Console).  
4. Store these in your credentials config.

---

### Wiz
1. Log into [Wiz](https://app.wiz.io/).  
2. Navigate to **Settings → Service Accounts → API Keys**.  
3. Generate a new **API Key**.  
4. Save the following:  
   - **API Key**.  
   - Base API URL: `https://api.wiz.io/`.  

---

### WooCommerce
1. Log into your WooCommerce store admin panel.  
2. Go to **WooCommerce → Settings → Advanced → REST API**.  
3. Create a new API Key:  
   - Choose a user.  
   - Set permissions to **Read** (or **Read/Write** if needed).  
4. Copy these:  
   - **Store URL** (e.g. `https://yourstore.com/wp-json/wc/v3/`).  
   - **Consumer Key**.  
   - **Consumer Secret**.  

---

### Shopify
1. Log into your [Shopify Admin](https://www.shopify.com/).  
2. Navigate to **Apps → Develop apps for your store**.  
3. Create a new app and configure Admin API scopes (e.g. `read_orders`, `read_products`).  
4. In the app → **API credentials**, collect:  
   - **Store URL** (e.g. `yourstore.myshopify.com/admin/api/2023-01/`).  
   - **Access Token** (generated by Shopify).  

---

## Spreadsheet Connectors (SPREADSHEET)

### Google Sheets
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select an existing **project**.
3. Enable the **Google Sheets API** & **Google Drive API** for your project.
4. Navigate to **APIs & Services → Credentials** and create:
   - **Service Account** (with Editor or Viewer role depending on needs).
   - Download the **Service Account JSON key file**.
5. Share your Google Sheet with the **Service Account email** (found in the JSON key, usually like `xxxx@project-id.iam.gserviceaccount.com`) and give at least **Viewer access**. 
6. Collect the following:
   - **Spreadsheet ID** - if your access is given to anyone with link (the long string in the sheet URL, e.g. `https://docs.google.com/spreadsheets/d/<spreadsheet_id>/edit`)
   - **Service Account JSON key file** If it needs to remain private (store it securely).
7. Store these in your credentials config.

---