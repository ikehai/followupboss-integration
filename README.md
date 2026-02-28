# Follow Up Boss Lead Integration

Python integration for adding leads to [Follow Up Boss](https://www.followupboss.com) CRM via their REST API.

## Features

- Create leads via the `/events` endpoint (triggers routing, automations, and notifications)
- Search existing contacts by name, email, or phone
- Add notes to contacts
- Create follow-up tasks
- List users/agents in the account

## Setup

### 1. Install dependencies

```bash
pip install requests
```

### 2. Set your API key

```bash
export FOLLOWUPBOSS_API_KEY=your_api_key_here
```

You can find your API key in Follow Up Boss under **Admin > API**.

### 3. Run the smoke test

```bash
python followupboss_integration.py
```

## Usage

```python
from followupboss_integration import create_lead, add_note, create_task

# Add a new buyer lead
result = create_lead(
    first_name="Jane",
    last_name="Doe",
    email="jane@example.com",
    phone="305-555-0000",
    source="Zillow",
    lead_type="Buyer",
    message="Interested in waterfront properties under $600k.",
    price_max=600000,
    tags=["waterfront", "motivated"],
)

person_id = result["person"]["id"]

# Add a note
add_note(person_id, body="Called and confirmed appointment for Thursday.")

# Create a follow-up task
create_task(person_id, name="Follow-up call", task_type="Call", due_date="2026-03-07")
```

## API Reference

| Function | Description |
|---|---|
| `create_lead(...)` | Add a new lead via `/events` (recommended) |
| `search_people(query)` | Search contacts by name/email/phone |
| `get_users()` | List all agents/users in the account |
| `add_note(person_id, body)` | Add a note to a contact |
| `create_task(person_id, name)` | Create a follow-up task |

## Authentication

Follow Up Boss uses HTTP Basic Auth. The API key is the username; the password is an empty string.

```
Authorization: Basic base64(API_KEY:)
```

## Notes

- Always use `/events` (not `/people`) to create new leads so automations fire correctly.
- The `X-System` header identifies the integration source in FUB's activity log.
- The `source` field controls which lead source label appears in FUB.
