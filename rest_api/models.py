# models.py – data structures (models) of the marketplace returns API
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

class Marketplace(str, Enum):
    """Marketplaces a return can come from"""
    AMAZON = "AMAZON"
    ZALANDO = "ZALANDO"

class ReturnStatus(str, Enum):
    """All statuses the return can have in the process."""
    NEW = "NEW"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    LABEL_SENT = "LABEL_SENT"
    IN_TRANSIT = "IN_TRANSIT"
    EXPIRED = "EXPIRED"
    RECEIVED = "RECEIVED"
    INSPECTED = "INSPECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    REFUNDED = "REFUNDED"
    CLOSED = "CLOSED"

# Which status may change into which. Key = current status, value = allowed next statuses.
ALLOWED_TRANSITIONS: dict[ReturnStatus, set[ReturnStatus]] = {
    ReturnStatus.NEW: {ReturnStatus.APPROVED, ReturnStatus.DENIED},
    ReturnStatus.APPROVED: {ReturnStatus.LABEL_SENT},
    ReturnStatus.LABEL_SENT: {ReturnStatus.IN_TRANSIT, ReturnStatus.RECEIVED, ReturnStatus.EXPIRED},
    ReturnStatus.IN_TRANSIT: {ReturnStatus.RECEIVED},
    ReturnStatus.RECEIVED: {ReturnStatus.INSPECTED},
    ReturnStatus.INSPECTED: {ReturnStatus.ACCEPTED, ReturnStatus.REJECTED, ReturnStatus.MANUAL_REVIEW},
    ReturnStatus.MANUAL_REVIEW: {ReturnStatus.ACCEPTED, ReturnStatus.REJECTED},
    ReturnStatus.ACCEPTED: {ReturnStatus.REFUNDED},
    ReturnStatus.REFUNDED: {ReturnStatus.CLOSED},
    ReturnStatus.REJECTED: {ReturnStatus.CLOSED},
    # End states: no further changes allowed
    ReturnStatus.DENIED: set(),
    ReturnStatus.EXPIRED: set(),
    ReturnStatus.CLOSED: set(),
}

class Item(BaseModel):
    """One article (in a return or an order)."""
    sku: str
    productName: str
    quantity: int = Field(gt=0)
    unitPrice: float = Field(ge=0)
    currency: str


class Customer(BaseModel):
    customerId: str
    email: str


class Return(BaseModel):
    """A return request as delivered by the marketplace."""
    returnId: str
    orderId: str
    marketplace: Marketplace
    status: ReturnStatus
    reason: str
    reasonText: str
    requestedAt: datetime
    updatedAt: datetime
    items: list[Item]
    customer: Customer
    returnLabelUrl: Optional[str] = None


class Order(BaseModel):
    """The original order the customer placed."""
    orderId: str
    marketplace: Marketplace
    orderedAt: datetime
    customer: Customer
    items: list[Item]
    totalAmount: float
    currency: str


class ReturnList(BaseModel):
    """Response for the list endpoint – wrapped in "data" like the professor's example."""
    data: list[Return]


class StatusUpdate(BaseModel):
    """What a client sends to change the status of a return."""
    status: ReturnStatus