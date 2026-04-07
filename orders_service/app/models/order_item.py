import uuid

from sqlalchemy import UUID, Column, ForeignKey, Integer, DECIMAL
from sqlalchemy.orm import relationship

from app.constants import ORDER_PRICE_MAX_DIGITS, ORDER_PRICE_DECIMAL_PLACES
from app.models.db import Base


class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(ORDER_PRICE_MAX_DIGITS, ORDER_PRICE_DECIMAL_PLACES), nullable=False)
    order = relationship("Order", back_populates="items", lazy="select")
