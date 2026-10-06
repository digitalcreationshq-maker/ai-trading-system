from fastapi import FastAPI

from app.broker.discovery import AccountHealth

app = FastAPI(title="AI Trading System", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "research", "orders_enabled": "false"}


@app.get("/account/status")
def account_status() -> dict[str, str]:
    return {
        "status": "NOT_CONNECTED",
        "mode": "research",
        "orders_enabled": "false",
        "message": "Read-only broker discovery adapter is not connected.",
    }
