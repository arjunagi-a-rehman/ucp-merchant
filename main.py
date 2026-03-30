from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from routes import profile, checkout, order, identity, products

description = """
### Universal Commerce Protocol (UCP) Sample Merchant API

This reference implementation demonstrates a UCP-compliant API for enabling **Agentic Commerce**. 
AI agents (like Gemini, Alexa, or Siri) can use these endpoints to perform secure, transaction-based actions on behalf of users.

**Key Capabilities:**
*   🚀 **Checkout**: Stateful transaction flow for AI agents.
*   📦 **Orders**: Standardized order status and tracking.
*   🔐 **Identity**: OAuth 2.0 based identity linking for agent authorization.

[Learn more about UCP](https://ucp.dev)
"""

tags_metadata = [
    {"name": "profile", "description": "UCP Discovery and Well-Known information."},
    {"name": "identity", "description": "OAuth 2.0 flow for account linking between AI agent and user."},
    {"name": "checkout", "description": "State-machine based checkout sessions."},
    {"name": "order", "description": "Post-purchase status and tracking."},
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
