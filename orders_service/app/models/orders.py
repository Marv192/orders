import uuid
from datetime import datetime

from sqlalchemy import Column, UUID, DECIMAL, DateTime, String
from sqlalchemy.orm import relationship

from app.constants import ORDER_PRICE_MAX_DIGITS, ORDER_PRICE_DECIMAL_PLACES, ORDER_STATUS_MAX_LENGTH
from app.models.db import Base


class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    total_price = Column(DECIMAL(ORDER_PRICE_MAX_DIGITS, ORDER_PRICE_DECIMAL_PLACES), nullable=False)
    cart_price = Column(DECIMAL(ORDER_PRICE_MAX_DIGITS, ORDER_PRICE_DECIMAL_PLACES), nullable=False)
    delivery_price = Column(DECIMAL(ORDER_PRICE_MAX_DIGITS, ORDER_PRICE_DECIMAL_PLACES), nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    items = relationship("OrderItem", back_populates="order", lazy="selectin", cascade="all, delete-orphan")
