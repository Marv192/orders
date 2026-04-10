from uuid import UUID

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import ORDER_SKIP, ORDER_LIMIT
from app.crud.order import order_crud
from app.models import get_async_session
from app.routers.dependencies import permission_required, get_current_user_id
from app.schemas.orders import OrderDB, OrderCreate, OrderInfo, OrderUpdate

orders = APIRouter()


@orders.post('/', status_code=status.HTTP_201_CREATED, response_model=OrderDB)
async def create_order(order_in: OrderCreate, session: AsyncSession = Depends(get_async_session),
                       _=Depends(permission_required('order.create'))):
    return await order_crud.create(db=session, obj_in=order_in)


@orders.get('/{order_id}', response_model=OrderInfo)
async def get_order(order_id: UUID, session: AsyncSession = Depends(get_async_session),
                    _=Depends(permission_required('order.read'))):
    return await order_crud.get(db=session, order_id=order_id)


@orders.get('/', response_model=list[OrderDB])
async def get_all_orders(user_id: UUID, skip: int = ORDER_SKIP, limit: int = ORDER_LIMIT,
                         session: AsyncSession = Depends(get_async_session),
                         _=Depends(permission_required('order.read'))):
    return await order_crud.get_all_orders_for_user(db=session, user_id=user_id, skip=skip, limit=limit)


@orders.patch('/{order_id}', response_model=OrderDB)
async def update_order(order_id: UUID, order_in: OrderUpdate, session: AsyncSession = Depends(get_async_session),
                       _=Depends(permission_required('order.update'))):
    db_order = await order_crud.get(db=session, order_id=order_id)
    return await order_crud.update(db=session, db_obj=db_order, obj_in=order_in)


@orders.delete('/{order_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: UUID, user_id=Depends(get_current_user_id),
                       session: AsyncSession = Depends(get_async_session),
                       _=Depends(permission_required('order.delete'))):
    await order_crud.delete_by_user(db=session, order_id=order_id, user_id=user_id)
    return None
