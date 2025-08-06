# Guide To Use

### For Desktop Odoo get in /local  
Step 1: Run all services in `docker-compose.yml`  
Step 2: Run `odoo_try.py` it uses the module `odoo_rpc_client.py` to get results  

### For running the flask app with all endpoints (recommended)  
Run `api/index.py` or test using my already deployed https://scai-odoo.vercel.app/

### For trying the gemini to query interface
run `/LLMtoQuery/Odoo/main.py` from Repo root

### For adding data to odoo
You can do it similar to my `/LLMtoQuery/Odoo/add_data.py` in Repo root

### .env structure:
For local odoo:  
`ODOO_LOCAL_URL=http://localhost:8069/jsonrpc`  
`ODOO_DB=<your db name>`  
`ODOO_EMAIL=<your email>@gmail.com`  
`ODOO_PASS=<suiii>`  
For odoo online and gemini to query assistance:  
`GEMINI_API_KEY=blahblahblah`  
`ODOO_URL=https://<your_domain>.odoo.com`  
`ODOO_KEY="blahbluh"`

### Available Endpoints
- `/`                         : Health check  
- `/auth`                    : Verify Odoo API connection  
- `/get/<model>`             : Fetch data from Odoo model (use `?fields=` and `limit=`)  
- `/schema/<model>`          : Get field schema of Odoo model  
- `/listsubtypes/<model>`    : List unique values of a field (use `?field=`)  
- `/gemini` (POST)           : Convert natural language to Odoo API call using Gemini
  
⚠︎ No `/tokenrefresh` needed : Odoo uses static UID & API key/password
