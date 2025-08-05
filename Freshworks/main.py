import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
import json 

load_dotenv()

FRESHDESK_DOMAIN = os.getenv("FRESHDESK_DOMAIN", "")
API_KEY = os.getenv("API_KEY", "")

headers = {
    "Content-Type": "application/json"
}

# 1. List contacts
def list_contacts():
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts"
    r = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=headers)
    print("📇 All Contacts:", r.status_code)
    print(r.json())

# 2. Create a test ticket
def create_ticket():
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets"
    data = {
        "description": "Test ticket from API",
        "subject": "API Test",
        "email": "demo.user@example.com",
        "priority": 1,
        "status": 2
    }
    r = requests.post(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=headers, json=data)
    print("🎫 Create Ticket:", r.status_code)
    print(r.json())
    return r.json().get("id")

# 3. Add a note to a ticket
def add_note(ticket_id):
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}/notes"
    data = {
        "body": "This is a note added via API",
        "private": True
    }
    r = requests.post(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=headers, json=data)
    print("📝 Add Note:", r.status_code)
    print(r.json())

# 4. Trigger plan-locked endpoint (archived ticket)
def test_archived_feature(ticket_id):
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/archived/{ticket_id}"
    r = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=headers)
    print("📦 Archived Ticket:", r.status_code)
    print(r.json())

def get_schema(endpoint, sample_count=1):
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/{endpoint}"
    response = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch {endpoint}: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    
    # If it's a list, take the first N
    if isinstance(data, list) and len(data) > 0:
        sample = data[:sample_count]
    elif isinstance(data, dict):
        sample = [data]
    else:
        print(f"⚠️ Unrecognized response format from {endpoint}")
        return
    
    print(f"Inferred Schema from {endpoint}:")
    for i, item in enumerate(sample):
        for key, value in item.items():
            print(f" - {key}: {type(value).__name__}")


def list_sub_product_types(endpoint):
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/{endpoint}"
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.get(url, auth=HTTPBasicAuth(API_KEY, 'x'), headers=headers)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            indices = list(range(len(data)))
            return json.dumps(indices)
        else:
            return json.dumps([])  # not a list-type response
    except Exception as e:
        return json.dumps({"error": str(e)})

# Examples
get_schema("tickets")
get_schema("contacts")

print("List sub product types of tickets: ", list_sub_product_types("tickets"))
# -------------------------------
# Run the test sequence
list_contacts()
ticket_id = create_ticket()
if ticket_id:
    add_note(ticket_id)
    test_archived_feature(ticket_id)
