import os
import gradio as gr
import requests
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
SAP_API_KEY = os.getenv("SAP_SANDBOX_APIKEY")  # Add this in your .env

# Constants
SAP_ENDPOINTS = {
    "API_SALES_CONTRACT_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_SALES_CONTRACT_SRV",
    "API_BUSINESS_PARTNER": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_BUSINESS_PARTNER",
    "API_PRODUCT_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_PRODUCT_SRV",
    "API_PRODUCT_STOCK_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_PRODUCT_STOCK_SRV",
    "API_SALES_ORDER_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_SALES_ORDER_SRV",
    "API_MATERIAL_STOCK_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_MATERIAL_STOCK_SRV",
    "API_WAREHOUSE_ORDER_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_WAREHOUSE_ORDER_SRV",
    "API_INBOUND_DELIVERY_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_INBOUND_DELIVERY_SRV",
    "API_OUTBOUND_DELIVERY_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_OUTBOUND_DELIVERY_SRV",
    "API_GL_ACCOUNT_BALANCE_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_GL_ACCOUNT_BALANCE_SRV",
    "API_INVOICE_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_INVOICE_SRV",
    "API_SUPPLIERINVOICE_PROCESS_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_SUPPLIERINVOICE_PROCESS_SRV",
    "API_BANK_ACCOUNT_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_BANK_ACCOUNT_SRV",
    "API_PURCHASEORDER_PROCESS_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV",
    "API_PURCHACE_ORDER_SRV": "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_PURCHACE_ORDER_SRV"
    # Add the rest similarly
}

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")

def clean_json_output(text):
    try:
        # if text.startswith("```json"):
        #     text = text.strip("```json").strip("`").strip()
        # elif text.startswith("```"):
            # text = text.strip("```").strip()

        if text.startswith("```json"):
            text = text[7:]  # Remove '```json\n'
        elif text.startswith("```"):
            text = text[3:]
        text = text.strip("`\n ")

        # Only take the first valid JSON block (in case there's extra junk)
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        if first_brace == -1 or last_brace == -1:
            raise ValueError("No valid JSON object found.")
        cleaned = text[first_brace:last_brace + 1]

        return json.loads(cleaned)
        # return json.loads(text)
    except Exception as e:
        raise ValueError(f"Failed to parse JSON: {e}\nRaw response: {text}")

def generate_sap_api(prompt):
    full_prompt = (
        "You are a helpful assistant that takes a user's natural language question "
        "and returns ONLY a valid JSON structure (no explanation, no markdown), "
        "representing the SAP OData REST API request. "
        "Output fields: 'api_name', 'endpoint', 'method', 'query_params'. "
        "Important:\n"
        "- The 'api_name' must match one of the official SAP service names (e.g., 'API_SALES_CONTRACT_SRV').\n"
        "- Do NOT use fields like 'ProductDescription' directly under 'A_Product'.\n"
        "- For product descriptions, use the navigation property 'to_ProductDescription' and apply $expand and $filter for Lang eq 'EN'.\n"
        "Do not wrap the JSON in code blocks. Return raw JSON only.\n\n"
        f"User: {prompt}\n\nAPI JSON:"
    )
    try:
        # Step 1: Ask Gemini
        response = model.generate_content(full_prompt)
        api_json = clean_json_output(response.text.strip())

        # Step 2: Construct full URL
        raw_endpoint = api_json["endpoint"] 
        for redundant in [
            "https://sandbox.api.sap.com/s4hanacloud",
            "/sap/opu/odata/sap/",
            "API_SALES_CONTRACT_SRV"
        ]:
            raw_endpoint = raw_endpoint.replace(redundant, "") # Clean any accidental repeated base path
        # Ensure it starts with a slash
        if not raw_endpoint.startswith("/"):
            raw_endpoint = "/" + raw_endpoint
        base_url = SAP_ENDPOINTS.get(api_json["api_name"])
        if not base_url:
            return "Error", f"Error: Unsupported API '{api_json['api_name']}'"
        url = base_url.rstrip("/") + api_json["endpoint"]
        method = api_json.get("method", "GET").upper()
        params = api_json.get("query_params", {})

        # Step 3: Make request
        headers = {
            "APIKey": SAP_API_KEY,
            "Accept": "application/json"
        }

        if method == "GET":
            r = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=params)
        else:
            return url, f"Unsupported method: {method}"

        if r.status_code >= 200 and r.status_code < 300:
            return r.url, json.dumps(r.json(), indent=2)
        else:
            return r.url, f"API Error {r.status_code}: {r.text[:500]}"

    except Exception as e:
        return "Error", f"Exception: {str(e)}"

def launch_interface():
    gr.Interface(
        fn=generate_sap_api,
        inputs=gr.Textbox(label="Ask your SAP API question"),
        outputs=[
            gr.Textbox(label="Actual API URL Used"),
            gr.Textbox(label="SAP JSON Response")
        ],
        title="Gemini to SAP Sales Contract Query"
    ).launch()

if __name__ == "__main__":
    prompt = "Get the 3 most recent sales contracts"
    result = generate_sap_api(prompt)
    print("Generated API Call:")
    print(result)

    launch_interface()