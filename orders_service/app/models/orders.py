import uuid
from datetime import datetime

from sqlalchemy import Column, UUID, DECIMAL, DateTime, Enum
from sqlalchemy.orm import relationship

from app.constants import ORDER_PRICE_MAX_DIGITS, ORDER_PRICE_DECIMAL_PLACES
from app.models.db import Base
from app.models.enums import OrderStatus


class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    total_price = Column(DECIMAL(ORDER_PRICE_MAX_DIGITS, ORDER_PRICE_DECIMAL_PLACES), nullable=False)
    cart_price = Column(DECIMAL(ORDER_PRICE_MAX_DIGITS, ORDER_PRICE_DECIMAL_PLACES), nullable=False)
    delivery_price = Column(DECIMAL(ORDER_PRICE_MAX_DIGITS, ORDER_PRICE_DECIMAL_PLACES), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    items = relationship("OrderItem", back_populates="order", lazy="selectin", cascade="all, delete-orphan")
