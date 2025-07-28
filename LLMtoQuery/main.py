import os
import gradio as gr
import requests
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

BASE = os.getenv("SERVICENOW_INSTANCE")
AUTH = (os.getenv("SERVICENOW_USER"), os.getenv("SERVICENOW_PASS"))

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")

def clean_json_output(text):
    try:
        # Handle code block fences
        if text.startswith("```json"):
            text = text.strip("```json").strip("`").strip()
        elif text.startswith("```"):
            text = text.strip("```").strip()
        return json.loads(text)
    except Exception as e:
        raise ValueError(f"Failed to parse JSON: {e}\nRaw response: {text}")

def generate_servicenow_api(prompt):
    full_prompt = (
        "You are a helpful assistant that takes a user's natural language question "
        "and returns ONLY a valid JSON structure (no explanation, no markdown), "
        "representing the ServiceNow REST API request: \n"
        "- Use 'endpoint', 'method', 'query_params' fields\n"
        "- Do not wrap the JSON in code blocks\n"
        "- Do not add comments or text\n"
        "- Output pure JSON only\n\n"
        f"User: {prompt}\n\nAPI JSON:"
    )
    try:
        # Step 1: Ask Gemini
        response = model.generate_content(full_prompt)
        api_json = clean_json_output(response.text.strip())

        # Step 2: Construct full URL
        url = BASE.rstrip("/") + api_json["endpoint"]

        # Step 3: Handle GET/POST
        method = api_json.get("method", "GET").upper()
        params = api_json.get("query_params", {})

        if method == "GET":
            r = requests.get(url, auth=AUTH, params=params)
        elif method == "POST":
            r = requests.post(url, auth=AUTH, json=params)
        else:
            return f"Unsupported method: {method}"

        if r.status_code >= 200 and r.status_code < 300:
            return r.url, json.dumps(r.json(), indent=2)
        else:
            return r.url, f"API Error {r.status_code}: {r.text}"
    
    except Exception as e:
        return f"Error: {str(e)}"

def launch_interface():
    gr.Interface(
        fn=generate_servicenow_api,
        inputs=gr.Textbox(label="Ask your question"),
        outputs=[
            gr.Textbox(label="Actual API URL Used"),
            gr.Textbox(label="ServiceNow JSON Response")
        ],
        title="Gemini to ServiceNow Query Agent"
    ).launch()

# Example usage
if __name__ == "__main__":
    prompt = "Get me the 5 most recent incidents assigned to john.doe"
    result = generate_servicenow_api(prompt)
    print("Generated API Call:")
    print(result)

    launch_interface()
