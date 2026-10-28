# main.py – mock REST API simulating the marketplaces (Amazon, Zalando) for return requests

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException

from rest_api.models import (
    ALLOWED_TRANSITIONS,
    Marketplace,
    Order,
    Return,
    ReturnList,
    ReturnStatus,
    StatusUpdate,
)

# Path to the mock data, built relative to this file so it works from any folder
DATA_FILE = Path(__file__).parent / "data" / "mock_data.json"


def load_data() -> tuple[dict[str, Return], dict[str, Order]]:
    """Read the JSON file and turn it into validated Return and Order objects."""
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    returns = {r["returnId"]: Return.model_validate(r) for r in raw["returns"]}
    orders = {o["orderId"]: Order.model_validate(o) for o in raw["orders"]}
    return returns, orders


# In-memory "database": filled once at startup, reset on every restart
RETURNS, ORDERS = load_data()

app = FastAPI(
    title="Marketplace Returns API (Mock)",
    description="Simulates the return interfaces of Amazon and Zalando for ShopEasy GmbH.",
    version="1.0.0",
)

@app.get("/returns", response_model=ReturnList)
def list_returns(
    status: Optional[ReturnStatus] = None,
    marketplace: Optional[Marketplace] = None,
) -> ReturnList:
    """List all returns, optionally filtered by status and/or marketplace."""
    result = list(RETURNS.values())
    if status is not None:
        result = [r for r in result if r.status == status]
    if marketplace is not None:
        result = [r for r in result if r.marketplace == marketplace]
    return ReturnList(data=result)

@app.get("/returns/{return_id}", response_model=Return)
def get_return(return_id: str) -> Return:
    """Get a single return by its returnId."""
    ret = RETURNS.get(return_id)
    if ret is None:
        raise HTTPException(status_code=404, detail=f"Return {return_id} not found")
    return ret


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str) -> Order:
    """Get the order data for an orderId."""
    order = ORDERS.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order

@app.patch("/returns/{return_id}/status", response_model=Return)
def update_status(return_id: str, update: StatusUpdate) -> Return:
    """Change the status of a return, following the allowed status transitions."""
    ret = RETURNS.get(return_id)
    if ret is None:
        raise HTTPException(status_code=404, detail=f"Return {return_id} not found")

    # Same status again (e.g. a duplicate message): nothing to do, answer OK (idempotent)
    if update.status == ret.status:
        return ret

    allowed = ALLOWED_TRANSITIONS[ret.status]
    if update.status not in allowed:
        allowed_text = ", ".join(sorted(s.value for s in allowed)) or "none (end state)"
        raise HTTPException(
            status_code=409,
            detail=f"Status change {ret.status.value} -> {update.status.value} not allowed. "
                   f"Allowed next statuses: {allowed_text}",
        )

    ret.status = update.status
    ret.updatedAt = datetime.now(timezone.utc)
    return ret