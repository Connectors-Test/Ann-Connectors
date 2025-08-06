# Guide To Use

Hey, 

This only connects to freshdesk, a freshworks app

### .env structure:
`FRESHDESK_DOMAIN = "<your domain>.freshdesk.com"`  
`API_KEY = <your api key>`

### For testing api locally (Not required)  
Run `main.py`

### For running the flask app with all endpoints (recommended)  
Run `api/index.py` or test using my already deployed https://smart-card-ai-ashy.vercel.app/

### For testing the demo web app  
Step 1: Run the server — `node <path to folder>/web/server.js` in terminal (assuming node is already installed)  
Step 2: Run the frontend — either locally by opening `index.html`, or go to[ https://scai-freshdesks.vercel.app/](http://smart-card-ai-3oob.vercel.app/)

### Available Endpoints
- /api/auth	                                      Check if API key and domain are valid  
- /api/data/<product>/<db>/<table>	              Get table data from Freshdesk  
- /api/listsubtypes/<endpoint>	                  List index positions of objects in list response  
- /api/fields/<endpoint>	                        List all field names available for that endpoint  

⚠︎ /tokenrefresh is not required since Freshdesk uses simple API key authentication (Basic Auth)
