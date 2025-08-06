# Guide to use

### The Flask api
run `api/app.py` or use [this link](https://scai-servicenow.vercel.app/) to test

### A web interface to test
run `web/app.py` or just visit [here](https://scai-servicenow-web.vercel.app/) to test

### Sample .env file 
```env
SERVICENOW_INSTANCE="https://<ur_domain>.service-now.com"  
SERVICENOW_USER="admin"  
SERVICENOW_PASS="blahblah"```

### Available Endpoints
- `/`                           : Health check  
- `/auth`                      : Verify ServiceNow connection  
- `/api/data/<endpoint>`       : Fetch data from ServiceNow (use `?sysparm_` params)  
- `/schema/<endpoint>`         : Get field schema from a ServiceNow endpoint  
- `/listsubproducttype/<path>` : List all field names from a ServiceNow resource  

⚠︎ No `/tokenrefresh` needed : Uses static basic auth (username + password)
