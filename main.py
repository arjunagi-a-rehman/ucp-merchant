from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from routes import profile, checkout, order, identity, products, agent_callback

description = """
### Universal Commerce Protocol (UCP) Merchant API

A self-describing API for **Agentic Commerce**. AI agents discover capabilities, link user identity, and transact — all from a single discovery URL.

**Start here:** `GET /.well-known/ucp` — returns all capabilities, flows, endpoints, and schemas.

**Key principles:**
- **Self-describing**: Every response includes `next_actions` telling the agent exactly what to do next
- **Actionable errors**: Error responses include the specific action and endpoint to fix the issue
- **Machine-readable flows**: The discovery endpoint defines complete purchase and auth flows with field mappings
- **Standard OAuth 2.0**: Identity linking via agent polling pattern (no browser automation needed)

**Typical agent flow:**
1. `GET /.well-known/ucp` — discover everything
2. Identity linking (OAuth + polling) — get a Bearer token
3. `GET /products` — browse catalog
4. `POST /checkout/sessions` — start checkout (response tells agent what's next)
5. `POST /checkout/sessions/{id}/update` — add buyer info (response tells agent what's next)
6. `POST /checkout/sessions/{id}/complete` — place order
7. `GET /orders/{id}` — track order
"""

tags_metadata = [
    {"name": "profile", "description": "UCP Discovery — the only URL an agent needs. Returns all capabilities, flows, endpoints, and schemas."},
    {"name": "identity", "description": "OAuth 2.0 identity linking with agent polling pattern. No browser automation required."},
    {"name": "checkout", "description": "State-machine checkout. Every response includes next_actions with the exact endpoint and fields needed."},
    {"name": "order", "description": "Order tracking with status-aware next_actions."},
    {"name": "products", "description": "Product catalog. Each product includes next_actions showing how to add it to a checkout."},
    {"name": "agent", "description": "Agent OAuth callback and session polling for seamless identity linking."},
]

app = FastAPI(
    title="UCP Merchant Sample API",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "UCP Developer Support",
        "url": "https://github.com/arjunagi-a-rehman/ucp-merchant",
    },
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>UCP Merchant Sample API</title>
            <style>
                body { font-family: sans-serif; text-align: center; padding-top: 50px; background: #fdfdfd; }
                .card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; display: inline-block; background: #fff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                a { color: #007bff; text-decoration: none; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Welcome to UCP Merchant Sample!</h1>
                <p>To explore the Universal Commerce Protocol API endpoints:</p>
                <p>👉 <a href="/docs">Go to Swagger UI (/docs)</a></p>
                <p>👉 <a href="/redoc">Go to Redoc UI (/redoc)</a></p>
                <hr/>
                <p>Discovery Endpoint: <a href="/.well-known/ucp">/.well-known/ucp</a></p>
            </div>
        </body>
    </html>
    """

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router)
app.include_router(checkout.router)
app.include_router(order.router)
app.include_router(identity.router)
app.include_router(products.router)
app.include_router(agent_callback.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
