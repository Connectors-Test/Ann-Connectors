# Unified API Proxy - Setup

This project provides a unified API proxy to query multiple services (databases, spreadsheets, DevOps/IoT tools, e-commerce platforms, and business applications) through a single Flask backend.

## Step 1: Clone Repository
```bash
git clone https://github.com/smart-card-ai/Connectors-Ann/
cd Connectors-Ann
```

## Step 2: Install Dependencies and Configure Environment variables
```bash
pip install -r requirements.txt
cp sqlite/.env.example sqlite/.env
```
See [CREDENTIALS_SETUP.md](CREDENTIALS_SETUP.md) for detailed instructions on how to get credentials for each supported service.

## Step 4: Initialize SQLite
Run all initialization scripts inside /sqlite/init or as required 

## Step 5: Run the Server
```bash
python main.py
```
The API will be available at `http://127.0.0.1:5000/`

## Step 6: Test with Postman
- Open Postman.
- Import the collections from /postman_exports/.
- Send requests to http://127.0.0.1:5000.