from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.constants import ORDER_PRICE_DECIMAL_PLACES, ORDER_PRICE_MAX_DIGITS, ORDER_STATUS_MAX_LENGTH, \
    ORDER_STATUS_MIN_LENGTH


class OrderItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    status: str = Field(max_length=ORDER_STATUS_MAX_LENGTH, min_length=ORDER_STATUS_MIN_LENGTH)
    items: list[OrderItemBase]


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[str] = Field(default=None, max_length=ORDER_STATUS_MAX_LENGTH, min_length=ORDER_STATUS_MIN_LENGTH)
    cart_price: Optional[Decimal] = Field(decimal_places=ORDER_PRICE_DECIMAL_PLACES, max_digits=ORDER_PRICE_MAX_DIGITS)
    total_price: Optional[Decimal] = Field(decimal_places=ORDER_PRICE_DECIMAL_PLACES, max_digits=ORDER_PRICE_MAX_DIGITS)
    delivery_price: Optional[Decimal] = Field(decimal_places=ORDER_PRICE_DECIMAL_PLACES, max_digits=ORDER_PRICE_MAX_DIGITS)


class OrderInfo(OrderBase):
    user_id: UUID
    cart_price: Decimal = Field(decimal_places=ORDER_PRICE_DECIMAL_PLACES, max_digits=ORDER_PRICE_MAX_DIGITS)
    total_price: Decimal = Field(decimal_places=ORDER_PRICE_DECIMAL_PLACES, max_digits=ORDER_PRICE_MAX_DIGITS)
    delivery_price: Decimal = Field(decimal_places=ORDER_PRICE_DECIMAL_PLACES, max_digits=ORDER_PRICE_MAX_DIGITS)


class OrderDB(OrderInfo):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
