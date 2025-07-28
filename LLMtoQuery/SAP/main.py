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
BASE = "https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_SALES_CONTRACT_SRV"

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")

def clean_json_output(text):
    try:
        if text.startswith("```json"):
            text = text.strip("```json").strip("`").strip()
        elif text.startswith("```"):
            text = text.strip("```").strip()
        return json.loads(text)
    except Exception as e:
        raise ValueError(f"Failed to parse JSON: {e}\nRaw response: {text}")

def generate_sap_api(prompt):
    full_prompt = (
        "You are a helpful assistant that takes a user's natural language request "
        "and returns ONLY a valid JSON object describing the SAP Sales Contract API call. "
        "Only provide the relative endpoint (after /API_SALES_CONTRACT_SRV), not the full URL. "
        "Use this structure:\n"
        "{\n  'endpoint': string (e.g. '/A_SalesContract?$top=5'),\n  'method': 'GET' or 'POST',\n  'query_params': optional object\n}\n"
        "Only return raw JSON. Do not explain or use markdown.\n\n"
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
        url = BASE.rstrip("/") + "/" + raw_endpoint.lstrip("/")
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
            return r.url, f"API Error {r.status_code}: {r.text}"

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
