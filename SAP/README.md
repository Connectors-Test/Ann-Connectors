# Guide To Use

### For running the flask app (recommended)  
Run `app.py` or test using my already deployed https://scai-sap.vercel.app/

### For trying the gemini to query interface
run `/LLMtoQuery/SAP/main.py` from Repo root

### .env structure: 
`GEMINI_API_KEY=blahblah`  
`SAP_SANDBOX_APIKEY=blacksheephaveyouanywool`  

### Available Endpoints
- `/`                         : Health check  
- `/auth`                    : Verify SAP API connection  
- `/api/data/<product>/<subproduct>`         : Get full data (use `?filters=`)  
- `/api/data/<product>/<subproduct>/<field>` : Get specific field data  
- `/api/schema/<product>/<subproduct>`       : Get schema (converted XML -> JSON)  
- `/api/listsubtypes/<product>`              : List all subproduct types

⚠︎ No `/tokenrefresh` needed : uses basic auth by API key
