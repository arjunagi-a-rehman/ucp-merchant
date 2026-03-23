# UCP Merchant Sample API

A reference implementation of the **Universal Commerce Protocol (UCP)** using FastAPI. This sample demonstrates how a merchant can expose standardized endpoints for AI Agents to perform discovery, identity linking, checkout, and order management.

## 🚀 Overview

The Universal Commerce Protocol (UCP) is an open standard that allows AI agents to interact with businesses directly. This repository provides a mock backend that implements the core UCP capabilities:

- **Identity Linking**: Securely link a user's AI platform account with your merchant store using OAuth 2.0.
- **Checkout**: A state-machine-based checkout flow (`incomplete` → `ready_for_complete` → `complete`).
- **Orders**: Post-purchase status tracking and fulfillment management.

## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tixt.dev/)
- **Runtime**: Python 3.12+
- **Dependency Management**: [uv](https://github.com/astral-sh/uv)
- **Security**: PyJWT (OAuth 2.0 Bearer tokens)

## 📁 Project Structure

```text
ucp-merchant/
├── main.py              # Entry point
├── security.py          # JWT authentication & authorization
├── test_api.py          # Automated end-to-end test suite
├── routes/
│   ├── profile.py       # Discovery (/.well-known/ucp)
│   ├── identity.py      # OAuth 2.0 & Identity Linking
│   ├── checkout.py      # Checkout Session management
│   └── order.py         # Order tracking
├── models/              # Pydantic schemas (UCP compliant)
└── services/            # In-memory mock business logic
```

## ⚙️ Getting Started

### 1. Install Dependencies
Ensure you have `uv` installed.
```bash
uv sync
```

### 2. Run the Server
```bash
uv run uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. You can explore the interactive documentation at `http://127.0.0.1:8000/docs`.

### 3. Run Automated Tests
This script simulates the entire UCP lifecycle (Discovery → Identity Linking → Checkout → Order).
```bash
uv run python test_api.py
```

## 🐳 Docker Support

If you prefer to run the project in a container:

```bash
# Build the image
docker build -t ucp-merchant .

# Run the container
docker run -p 8000:8000 ucp-merchant
```

## 🔒 Security Model

All protected endpoints (`/checkout` and `/orders`) require a valid **Bearer Token** obtained through the Identity Linking handshake.

1. **Discovery**: The agent finds the OAuth config at `/.well-known/oauth-authorization-server`.
2. **Authorize**: Agent redirects user to `/oauth/authorize` to get a `code`.
3. **Token**: Agent exchanges `code` for a signed **JWT** at `/oauth/token`.
4. **Access**: The agent uses the JWT to act on behalf of the user for all commerce operations.

## 📜 Contributing
This is a sample project for educational and reference purposes. Feel free to fork and adapt it for your own UCP integrations!

---
*Developed as a reference for Universal Commerce Protocol (UCP) developers.*
