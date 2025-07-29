import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

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

# -------------------------------
# Run the test sequence
list_contacts()
ticket_id = create_ticket()
if ticket_id:
    add_note(ticket_id)
    test_archived_feature(ticket_id)
