# UCP Sample REST API Walkthrough

We have successfully implemented the Sample REST API for the Universal Commerce Protocol (UCP), including both **Checkout** and **Order** capabilities.

### Framework
The project uses `uv` for dependency management and environment creation, and `FastAPI` to serve the API endpoints as specified in the plan.

### Project Layout
```
ucp-merchant/
├── main.py
├── test_api.py (Auto-validation python script)
├── pyproject.toml
├── uv.lock
├── routes/
│   ├── profile.py
│   ├── checkout.py
│   └── order.py
├── models/
│   ├── checkout.py
│   └── order.py
├── services/
│   ├── checkout.py
│   └── order.py
```

### Endpoints
The following exact endpoints have been created:
- `GET /.well-known/ucp`: Returns the merchant profile supporting the `checkout` and `order` capabilities.

**Checkout Flow:**
- `POST /checkout/sessions`: Creates a new session from line items. Initial status is `incomplete`.
- `POST /checkout/sessions/{id}/update`: Submits buyer information (email, shipping address, payment method) which automatically transitions the status to `ready_for_complete`.
- `POST /checkout/sessions/{id}/complete`: Validates that the session is ready and transitions the status to `complete`. After completion, the underlying order is generated.

**Order Capability:**
- `GET /orders/{id}`: AI agents use this endpoint to fetch the status of an existing order and its tracking link.

### Testing
We automatically verified the happy path using an automated script (`test_api.py`) that spins up the FastAPI application. All responses matched the UCP lifecycle flow: the agent queries the profile, creates the session, updates the shipping details, completes the transaction, and tracks the generated order.

You can manually run the server and explore the OpenAPI interface by running within the folder:

```bash
cd /Users/admin/Desktop/coppal/ai-ucp/ucp-merchant
uv run uvicorn main:app --reload
```
Then navigate to `http://127.0.0.1:8000/docs`.
