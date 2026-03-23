import time
import requests
import subprocess
import json
import sys

# use uv to run server
server = subprocess.Popen(["uv", "run", "uvicorn", "main:app", "--port", "8000"])
time.sleep(2)

HEADERS = {}

try:
    print("\n--- 1. Discovery (UCP Profile) ---")
    res = requests.get("http://127.0.0.1:8000/.well-known/ucp")
    print(res.status_code, res.json())
    assert res.status_code == 200
    assert "dev.ucp.common.identity_linking" in res.json()["capabilities"]

    print("\n--- 2. OAuth Discovery ---")
    res = requests.get("http://127.0.0.1:8000/.well-known/oauth-authorization-server")
    oauth_config = res.json()
    print(res.status_code, oauth_config)
    
    # 1. Authorize: In real world, user logs in here. 
    # Use the discovered endpoints
    print("\n--- 3. Identity Linking Handshake (Authorize) ---")
    auth_params = {
        "client_id": "agent_abc",
        "redirect_uri": "http://127.0.0.1:8000/callback",
        "response_type": "code"
    }
    # allow_redirects=False lets us see the code in the redirected URL easily
    res = requests.get(oauth_config["authorization_endpoint"], params=auth_params, allow_redirects=False)
    redirect_url = res.headers["Location"]
    auth_code = redirect_url.split("code=")[1].split("&")[0]
    print(f"Auth Code Received: {auth_code}")

    # 2. Exchange code for token
    print("\n--- 4. Identity Linking Handshake (Token) ---")
    token_url = oauth_config["token_endpoint"]
    res = requests.post(token_url, data={"grant_type": "authorization_code", "code": auth_code})
    token_data = res.json()
    access_token = token_data["access_token"]
    print(f"Access Token: {access_token}")

    # Set the HEADERS to use the standard OAuth Bearer token
    HEADERS = {"Authorization": f"Bearer {access_token}"}

    print("\n--- 5. Create Session (PROTECTED via Bearer Token) ---")
    payload = {
        "line_items": [
            {"id": "item-1", "name": "Basic Ticket", "quantity": 1, "price": 49.99}
        ]
    }
    res = requests.post("http://127.0.0.1:8000/checkout/sessions", json=payload, headers=HEADERS)
    session = res.json()
    print(res.status_code, session)
    assert res.status_code == 200
    assert session["status"] == "incomplete"
    session_id = session["id"]

    print("\n--- 6. Update Session (PROTECTED) ---")
    update_payload = {
        "buyer": {
            "email": "agent@example.com",
            "shipping_address": {"city": "New York", "state": "NY"},
            "payment_method": "credit_card"
        }
    }
    res = requests.post(f"http://127.0.0.1:8000/checkout/sessions/{session_id}/update", json=update_payload, headers=HEADERS)
    session = res.json()
    print(res.status_code, session)
    assert res.status_code == 200
    assert session["status"] == "ready_for_complete"

    print("\n--- 7. Complete Session (PROTECTED) ---")
    res = requests.post(f"http://127.0.0.1:8000/checkout/sessions/{session_id}/complete", headers=HEADERS)
    session = res.json()
    print(res.status_code, session)
    assert res.status_code == 200
    assert session["status"] == "complete"
    
    # Extract order ID to track it
    order_id = f"ORD-{session_id[:8]}"

    print("\n--- 8. Get Order Status (PROTECTED) ---")
    res = requests.get(f"http://127.0.0.1:8000/orders/{order_id}", headers=HEADERS)
    order = res.json()
    print(res.status_code, order)
    assert res.status_code == 200
    assert order["status"] == "processing"
    assert "tracking_url" in order

    print("\n✅ All tests passed!")
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    sys.exit(1)
finally:
    server.terminate()
