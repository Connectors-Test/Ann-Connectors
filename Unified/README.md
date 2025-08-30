# Unified API Proxy - Setup

This project provides a unified API proxy to query multiple services (databases, spreadsheets, DevOps/IoT tools, e-commerce platforms, and business applications) through a single Flask backend.

## Step 1: Clone Repository
```bash
git clone https://github.com/smart-card-ai/Connectors-Ann/
cd Connectors-Ann/Unified
```

## Step 2: Install Dependencies and Configure Environment variables
```bash
pip install -r requirements.txt
```
Then use your own credentials using the .env.example file variables or request me access to my credentials (which may contain outdated ones).
See [CREDENTIALS_SETUP.md](CREDENTIALS_SETUP.md) for detailed instructions on how to get credentials for each supported service.

## Step 4: Initialize SQLite
Run all initialization scripts inside /sqlite/init or as required 
Note: Remember to run these init scripts using the following command.
```bash
cd .. # to ensure it runs from the Connectors-Ann directory
python -m Unified.sqlite.init.applications
python -m Unified.sqlite.init.databases
python -m Unified.sqlite.init.devops_and_iot
python -m Unified.sqlite.init.ecommerce
python -m Unified.sqlite.init.spreadsheet
```

## Step 5: Run the Server
```bash
cd Unified/sqlite # ensure every other files except ones in init runs from this path
python "c:/Program Files/Python312/Connectors-Ann/Unified/main.py" # change according to your path
```
The API will be available at `http://127.0.0.1:5000/`

## Step 6: Test with Postman
- Open Postman.
- Import the collections from /postman_exports/.
- Send requests to http://127.0.0.1:5000.