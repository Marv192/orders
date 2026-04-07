from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import ORDER_SKIP, ORDER_LIMIT
from app.crud.base import CRUDBase
from app.kafka.events import send_order_created_event, send_order_updated_event
from app.models import Order, OrderItem
from app.schemas.orders import OrderCreate, OrderUpdate, OrderDB
from app.utils.price import get_delivery_price, get_total_price, get_cart_price


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: OrderCreate) -> Order:
        items_data = obj_in.items
        order_data = obj_in.model_dump(exclude={"items"})
        order_data['cart_price'] = get_cart_price(items_data)
        order_data['delivery_price'] = get_delivery_price()
        order_data['total_price'] = get_total_price(order_data['cart_price'], order_data['delivery_price'])

        db_order = Order(**order_data)

        for item_schema in items_data:
            db_item = OrderItem(**item_schema.model_dump())
            db_order.items.append(db_item)

        db.add(db_order)
        await db.commit()
        await db.refresh(db_order, attribute_names=["items"])

        order_db = OrderDB.model_validate(db_order)
        send_order_created_event(order_db)
        return db_order

    async def get(self, db: AsyncSession, *, order_id: UUID) -> Order:
        order_info = await super().get(db=db, obj_id=order_id)

        if not order_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        return order_info

    async def get_all_orders_for_user(self, db: AsyncSession, *, user_id: UUID, skip: int = ORDER_SKIP,
                                      limit: int = ORDER_LIMIT) -> list[Order]:
        stmt = select(self.model).where(self.model.user_id == user_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, db: AsyncSession, *, db_obj: Order, obj_in: OrderUpdate) -> Order:
        updated_order = await super().update(db=db, db_obj=db_obj, obj_in=obj_in)

        order_updated = OrderDB.model_validate(updated_order)
        send_order_updated_event(order_updated)

        return updated_order

    async def delete(self, db: AsyncSession, *, order_id: UUID) -> Optional[Order]:
        result = await super().delete(db=db, obj_id=order_id)

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        return result


order_crud = CRUDOrder(Order)
