from fastapi import FastAPI
from routes import profile, checkout, order, identity

app = FastAPI(title="UCP Merchant Sample API")

app.include_router(profile.router)
app.include_router(checkout.router)
app.include_router(order.router)
app.include_router(identity.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
