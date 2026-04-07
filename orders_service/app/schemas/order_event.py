import uuid
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.orders import OrderDB


class EventMetadata(BaseModel):
    event_id: UUID = Field(default_factory=uuid.uuid4)
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.now)


class OrderEvent(BaseModel):
    metadata: EventMetadata = Field(default_factory=EventMetadata)
    data: OrderDB
