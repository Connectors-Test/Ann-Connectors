import os
import gradio as gr
import requests
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
ODOO_URL = os.getenv("ODOO_URL")
ODOO_KEY = os.getenv("ODOO_KEY")

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

def generate_odoo_api(prompt):
    full_prompt = (
        "You are an Odoo API assistant. Take the user's query and convert it into a JSON object.\n"
        "Example:\n"
        "{\n"
        "  'model': 'product.product',\n"
        "  'method': 'search_read',\n"
        "  'args': [[['list_price', '>', 50]]],\n"
        "  'kwargs': { 'fields': ['id', 'name', 'list_price'], 'limit': 5}\n"
        "}\n"
        "Only return raw JSON. Do not include explanations or markdown.\n\n"
        f"User: {prompt}\n\nAPI JSON:"
    )
    try:
        # Step 1: Ask Gemini
        response = model.generate_content(full_prompt)
        api_json = clean_json_output(response.text.strip())

        # Step 2: Construct full URL
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "id": 1,
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    "smartcardai",  # DB name
                    2,              # UID
                    ODOO_KEY,       # API key / password
                    api_json["model"],
                    api_json["method"],
                    api_json.get("args", []),  # usually: [domain]
                    api_json.get("kwargs", {})  # optional: {"fields": [...]}
                ]
            }
        }

        # Odoo URL
        url = f"{ODOO_URL}/jsonrpc"

        # Send POST request
        r = requests.post(url, headers=headers, json=payload)

        if r.status_code >= 200 and r.status_code < 300:
            return json.dumps(r.json(), indent=2), json.dumps(payload, indent=2)
        else:
            return f"API Error {r.status_code}: {r.text}", json.dumps(payload, indent=2)

    except Exception as e:
        return f"Exception: {str(e)}", "Error"

def launch_interface():
    gr.Interface(
        fn=generate_odoo_api,
        inputs=gr.Textbox(label="Ask your Odoo API question"),
        outputs=[
            gr.Textbox(label="Odoo Response"),
            gr.Textbox(label="Odoo JSON-RPC Payload")
        ],
        title="Gemini to Odoo Query"
    ).launch()

if __name__ == "__main__":
    prompt = "Get the 3 most recent sales leads"
    payload, response = generate_odoo_api(prompt)
    print("Generated Payload:")
    print(payload)
    print("Response:")
    print(response)

    launch_interface()
