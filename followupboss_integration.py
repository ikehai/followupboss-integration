"""
Follow Up Boss - Lead Ingestion Integration
============================================
Adds new leads to Follow Up Boss via the /events endpoint.
The events endpoint triggers lead routing, action plans, and
agent notifications automatically.

Authentication:
    HTTP Basic Auth — API key as username, empty string as password.

Usage:
    Set the FOLLOWUPBOSS_API_KEY environment variable, then call
    create_lead() with the lead details.

Example:
    python followupboss_integration.py
"""

import os
import json
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://api.followupboss.com/v1"
API_KEY = os.environ.get("FOLLOWUPBOSS_API_KEY", "")  # Set via env variable


def get_auth():
    """Return Basic Auth tuple for Follow Up Boss API."""
    return (API_KEY, "")


def get_headers():
    """Return default headers for all API requests."""
    return {
        "Content-Type": "application/json",
        "X-System": "Nebula",
        "X-System-Key": API_KEY,
    }


# ---------------------------------------------------------------------------
# Lead Creation
# ---------------------------------------------------------------------------

def create_lead(
    first_name: str,
    last_name: str,
    email: str = None,
    phone: str = None,
    source: str = "API",
    lead_type: str = "Buyer",
    message: str = "",
    price_min: int = None,
    price_max: int = None,
    tags: list = None,
    assigned_to: str = None,
) -> dict:
    """
    Create a new lead in Follow Up Boss via the /events endpoint.

    Args:
        first_name:   Lead's first name.
        last_name:    Lead's last name.
        email:        Lead's email address.
        phone:        Lead's phone number.
        source:       Lead source label (e.g., "Referral", "Zillow", "Website").
        lead_type:    Contact type (e.g., "Buyer", "Seller", "Tenant").
        message:      Free-text inquiry message or notes.
        price_min:    Minimum budget/price.
        price_max:    Maximum budget/price.
        tags:         Additional tag strings to apply. "AI Created" is always added automatically.
        assigned_to:  Agent email address to assign the lead to.

    Returns:
        Parsed JSON response from the API.

    Raises:
        requests.HTTPError: If the API returns a non-2xx status code.
    """
    person = {
        "firstName": first_name,
        "lastName": last_name,
    }
    if email:
        person["emails"] = [{"value": email}]
    if phone:
        person["phones"] = [{"value": phone}]

    payload = {
        "source": source,
        "system": "Nebula",
        "type": lead_type,
        "person": person,
        "message": message,
    }

    if price_min is not None:
        payload["priceMin"] = price_min
    if price_max is not None:
        payload["priceMax"] = price_max

    # Always include the AI-created tag; merge with any caller-supplied tags
    default_tags = ["AI Created"]
    merged_tags = list(set(default_tags + (tags or [])))
    payload["tags"] = merged_tags

    if assigned_to:
        payload["assigned"] = assigned_to

    response = requests.post(
        f"{BASE_URL}/events",
        auth=get_auth(),
        headers=get_headers(),
        json=payload,
    )
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Helper Utilities
# ---------------------------------------------------------------------------

def get_users() -> list:
    """Return a list of all users/agents in the Follow Up Boss account."""
    response = requests.get(
        f"{BASE_URL}/users",
        auth=get_auth(),
        headers=get_headers(),
    )
    response.raise_for_status()
    return response.json().get("users", [])


def search_people(query: str) -> list:
    """Search for existing contacts by name, email, or phone."""
    response = requests.get(
        f"{BASE_URL}/people",
        auth=get_auth(),
        headers=get_headers(),
        params={"q": query, "limit": 10},
    )
    response.raise_for_status()
    return response.json().get("people", [])


def add_note(person_id: int, body: str, subject: str = "") -> dict:
    """Add a note to an existing contact."""
    payload = {"personId": person_id, "body": body, "subject": subject}
    response = requests.post(
        f"{BASE_URL}/notes",
        auth=get_auth(),
        headers=get_headers(),
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def create_task(person_id: int, name: str, task_type: str = "Call", due_date: str = None) -> dict:
    """Create a follow-up task for a contact."""
    payload = {"personId": person_id, "name": name, "type": task_type}
    if due_date:
        payload["dueDate"] = due_date
    response = requests.post(
        f"{BASE_URL}/tasks",
        auth=get_auth(),
        headers=get_headers(),
        json=payload,
    )
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Example / Smoke Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Follow Up Boss Integration -- Smoke Test")
    print("=" * 50)

    result = create_lead(
        first_name="John",
        last_name="Smith",
        email="jsmith@email.com",
        phone="305-555-1234",
        source="Referral",
        lead_type="Buyer",
        message="Looking for a 3 bedroom home under $400,000. Referred by Maria.",
        price_max=400000,
    )

    print("Lead created successfully!")
    print(json.dumps(result, indent=2))
