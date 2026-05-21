import logging
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

logger = logging.getLogger(__name__)


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    async def create_by_user(self, db: AsyncSession, *, obj_in: OrderCreate, user_id: UUID) -> Order:
        items_data = obj_in.items
        order_data = obj_in.model_dump(exclude={"items"})
        order_data['user_id'] = user_id
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
        logger.info("Order created", extra={"order_id": str(order_db.id)})
        return db_order

    async def get(self, db: AsyncSession, *, order_id: UUID) -> Order:
        order_info = await super().get(db=db, obj_id=order_id)

        if not order_info:
            logger.warning("Order not found", extra={"order_id": str(order_id)})
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
        logger.info("Order updated", extra={
            "order_id": str(order_updated.id),
            "new_status": order_updated.status,
            "new_cart_price": order_updated.cart_price,
            "new_delivery_price": order_updated.delivery_price,
            "new_total_price": order_updated.total_price
        })

        return updated_order

    async def delete_by_user(self, db: AsyncSession, *, order_id: UUID, user_id: UUID) -> Order:
        order = await order_crud.get(db=db, order_id=order_id)

        if str(order.user_id) != str(user_id):
            logger.warning("Order delete failed: access denied", extra={
                "order_id": str(order_id),
                "order_user_id": str(order.user_id)
            })
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        await db.delete(order)
        await db.commit()
        logger.info("Order deleted", extra={"order_id": str(order_id)})
        return order


order_crud = CRUDOrder(Order)
