# UCP Merchant API

A reference implementation of the **Universal Commerce Protocol (UCP)** — an open standard ([ucp.dev](https://ucp.dev)) that lets AI agents discover, authenticate, and transact with online merchants.

**Live API**: [ucp.c0a1.in](https://ucp.c0a1.in) | **Live Store**: [ucp-demo-1f0cf.web.app](https://ucp-demo-1f0cf.web.app) | **Live Agent**: [Cloud Run](https://ucp-shopping-agent-189730860966.us-central1.run.app)

![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green?logo=fastapi) ![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python) ![UCP](https://img.shields.io/badge/UCP-1.0-orange)

---

## Architecture

```
[AI Agent (Gemini/Claude/GPT)]
        |
        v
[UCP Merchant API (this repo)]  ←→  [Storefront API (Next.js + Firebase)]
        |                                        |
        v                                        v
  /.well-known/ucp                         [Firestore Database]
  /oauth/authorize                         [Firebase Auth]
  /checkout/sessions                       [Razorpay Payments]
  /orders
```

The UCP merchant is a **protocol layer** — it proxies to the storefront's API routes. It has zero database dependencies. Any AI agent that speaks UCP can use it.

---

## Spec Compliance

Verified against the official [UCP specification](https://ucp.dev/specification/).

### What's Implemented

| Area | Spec Requirement | Status | Notes |
|------|-----------------|--------|-------|
| Discovery `/.well-known/ucp` | RFC 8615 compliant manifest | ✅ | Includes flows, endpoints, field mappings, OAuth config |
| Checkout State Machine | `incomplete → ready_for_complete → complete` | ✅ | Exact match with spec |
| Checkout Endpoints | Create, retrieve, update, complete | ✅ | POST create, GET retrieve, POST update, POST complete |
| Bearer Token Auth | Required for protected endpoints | ✅ | JWT with HS256 |
| Line Items Schema | id, name, quantity, price | ✅ | Matches spec |
| Buyer Info Schema | email, shipping_address, payment_method | ✅ | Matches spec |
| Order Management | GET order by ID, list orders | ✅ | Basic CRUD |
| OAuth 2.0 Identity Linking | Authorization code flow | ✅ | Firebase-based with agent polling pattern |
| Product Catalog | List and get products | ✅ | Proxied from storefront |
| HTTPS + JSON | Required transport | ✅ | |

### Enhancements Beyond Spec

| Feature | Description |
|---------|-------------|
| `next_actions` in responses | Every checkout/order response tells the agent exactly what to do next — endpoint, method, required fields, and examples |
| Actionable error messages | Errors include `action`, `steps`, and `discovery_url` so agents can self-recover |
| Machine-readable flow definitions | Discovery endpoint includes complete flow definitions with field mappings (`maps_to: "product.id"`) |
| Agent polling for OAuth | Instead of requiring browser automation, agents poll `/agent/session/{id}` after user signs in — seamless UX |

### Not Yet Implemented

| Area | Spec Requirement | Priority | Notes |
|------|-----------------|----------|-------|
| PUT for session update | Spec uses PUT, we use POST | Low | Functionally identical |
| OAuth Scopes | `ucp:scopes:checkout_session`, etc. | Medium | All endpoints currently use a single scope |
| Token Revocation | RFC 7009 `POST /oauth/revoke` | Medium | Tokens expire after 1 hour |
| Payment Token Exchange | Core capability in spec | High | Currently payment_method is a string, not a tokenized payment instrument |
| Webhooks | Order lifecycle events (shipped, delivered) | Medium | Orders are polling-based only |
| Multi-transport | MCP + A2A bindings | Low | REST-only for now |
| Extensions System | Discounts, loyalty, etc. | Low | Not implemented |
| Account Creation Flow | Create account during identity linking | Low | Assumes user already has a Google account |

**Overall compliance: ~70%** — core commerce flow is fully spec-compliant. Gaps are in OAuth formality, payment tokens, and multi-transport.

---

## API Endpoints

### Discovery (no auth)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/.well-known/ucp` | GET | UCP discovery — capabilities, flows, endpoints, schemas |
| `/.well-known/oauth-authorization-server` | GET | OAuth config (RFC 8414) |

### Products (no auth)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/products` | GET | List all products (optional `?category=` filter) |
| `/products/{id}` | GET | Get product details |

### Identity Linking

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/oauth/authorize` | GET | Start OAuth flow — redirects to storefront login |
| `/oauth/token` | POST | Exchange auth code for JWT |
| `/agent/callback` | GET | OAuth callback — stores token in Firestore |
| `/agent/session/{id}` | GET | Poll for auth token (agent polling pattern) |

### Checkout (Bearer token required)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/checkout/sessions` | POST | Create session (→ `incomplete`) |
| `/checkout/sessions/{id}` | GET | Get session with `next_actions` |
| `/checkout/sessions/{id}/update` | POST | Add buyer info (→ `ready_for_complete`) |
| `/checkout/sessions/{id}/complete` | POST | Place order (→ `complete`) |

### Orders (Bearer token required)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/orders` | GET | List user's orders |
| `/orders/{id}` | GET | Get order with `next_actions` |

---

## Self-Describing API

Every response includes guidance for AI agents:

### next_actions (Checkout)
```json
{
  "id": "abc-123",
  "status": "incomplete",
  "next_actions": [{
    "action": "update_buyer",
    "method": "POST",
    "endpoint": "/checkout/sessions/abc-123/update",
    "required_fields": ["buyer.email", "buyer.shipping_address.city", "buyer.shipping_address.state"],
    "example": {
      "buyer": {
        "email": "user@example.com",
        "shipping_address": {"city": "Bangalore", "state": "KA"},
        "payment_method": "razorpay"
      }
    }
  }]
}
```

### Actionable Errors
```json
{
  "error": "not_authenticated",
  "action": "Initiate identity linking via the OAuth flow",
  "steps": [
    "Generate a session_id (UUID)",
    "Redirect user to: GET /oauth/authorize?client_id={agent_id}&redirect_uri=/agent/callback?session_id={session_id}",
    "Poll GET /agent/session/{session_id} every 2 seconds until status='linked'",
    "Use the returned token as: Authorization: Bearer {token}"
  ],
  "discovery_url": "/.well-known/ucp"
}
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| Runtime | Python 3.12+ |
| Auth | PyJWT (HS256) |
| HTTP Client | httpx (proxies to storefront) |
| Dependency Manager | uv |

## Project Structure

```
ucp-merchant/
├── main.py                     # FastAPI app + OpenAPI config
├── config.py                   # STOREFRONT_URL, API keys
├── security.py                 # JWT auth + actionable errors
├── routes/
│   ├── profile.py              # /.well-known/ucp discovery
│   ├── identity.py             # OAuth 2.0 identity linking
│   ├── checkout.py             # Checkout sessions + next_actions
│   ├── order.py                # Order tracking + next_actions
│   ├── products.py             # Product catalog proxy
│   └── agent_callback.py       # Agent OAuth callback + session polling
├── models/
│   ├── checkout.py             # LineItem, BuyerInfo, CheckoutSession
│   └── order.py                # Order model
├── services/
│   ├── checkout.py             # Checkout service (proxies to storefront)
│   └── order.py                # Order service (proxies to storefront)
└── test_api.py                 # E2E test suite
```

## Getting Started

### Install
```bash
uv sync
```

### Run
```bash
uv run uvicorn main:app --reload
```

API at `http://127.0.0.1:8000` | Swagger at `http://127.0.0.1:8000/docs`

### Test
```bash
uv run python test_api.py
```

### Docker
```bash
docker build -t ucp-merchant .
docker run -p 8000:8000 ucp-merchant
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STOREFRONT_URL` | `https://ucp-demo-1f0cf.web.app` | Backend storefront URL |
| `STOREFRONT_API_KEY` | `ucp-demo-internal-key-2024` | Internal API key |
| `UCP_API_BASE` | `http://127.0.0.1:8000` | Self-referencing base URL |

---

## Related Repos

| Repo | Description |
|------|-------------|
| [ucp-demo-store](https://github.com/arjunagi-a-rehman/ucp-demo-store) | Next.js e-commerce storefront with Firebase + Razorpay |
| [UCP Spec](https://github.com/Universal-Commerce-Protocol/ucp) | Official UCP specification |

## License

MIT
