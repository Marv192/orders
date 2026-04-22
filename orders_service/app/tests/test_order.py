from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from fastapi import HTTPException

from app.crud.order import order_crud
from app.models import Order
from app.schemas.orders import OrderCreate, OrderItemBase, OrderUpdate


@pytest.fixture()
def mock_db_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.scalar = AsyncMock()
    return session


@pytest.fixture()
def mock_order_items():
    return [
        OrderItemBase(
            product_id=UUID('123e4567-e89b-12d3-a456-426614174003'),
            quantity=2,
            unit_price=Decimal('4.00')
        )
    ]


@pytest.fixture()
def mock_order(mock_order_items):
    order = MagicMock(spec=Order)
    order.id = UUID('123e4567-e89b-12d3-a456-426614174001')
    order.user_id = UUID('123e4567-e89b-12d3-a456-426614174002')
    order.total_price = Decimal('10.00')
    order.cart_price = Decimal('8.00')
    order.delivery_price = Decimal('2.00')
    order.status = 'test status'
    order.created_at = datetime.now()
    order.items = mock_order_items
    return order


@pytest.fixture()
def mock_result():
    result = MagicMock()
    return result


class TestOrder:
    @pytest.mark.asyncio
    async def test_create_order_success(self, mock_db_session, mock_order):
        async def refresh_side_effect(obj, attribute_names=None):
            obj.id = UUID('123e4567-e89b-12d3-a456-426614174001')
            obj.created_at = datetime.now()

        order_data = OrderCreate(status=mock_order.status, items=mock_order.items)
        mock_db_session.refresh.side_effect = refresh_side_effect

        with patch('app.crud.order.send_order_created_event') as mock_send_event:
            result = await order_crud.create_by_user(db=mock_db_session, obj_in=order_data,
                                                     user_id=UUID('123e4567-e89b-12d3-a456-426614174002'))

        assert result.id == mock_order.id
        assert result.status == mock_order.status
        assert len(result.items) == len(mock_order.items)
        mock_db_session.commit.assert_called_once()
        mock_send_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_order_success(self, mock_db_session, mock_order, mock_result):
        mock_result.scalar_one_or_none.return_value = mock_order
        mock_db_session.execute.return_value = mock_result

        result = await order_crud.get(db=mock_db_session, order_id=mock_order.id)

        assert result.id == mock_order.id
        assert result.status == mock_order.status
        assert result.created_at == mock_order.created_at
        assert result.total_price == mock_order.total_price

    @pytest.mark.asyncio
    async def test_get_order_not_found(self, mock_db_session, mock_order, mock_result):
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await order_crud.get(db=mock_db_session, order_id=mock_order.id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == 'Order not found'

    @pytest.mark.asyncio
    async def test_get_all_orders_for_user_success(self, mock_db_session, mock_order, mock_result):
        mock_result.scalars.return_value.all.return_value = [mock_order]
        mock_db_session.execute.return_value = mock_result

        result = await order_crud.get_all_orders_for_user(db=mock_db_session, user_id=mock_order.user_id)

        assert result == [mock_order]

    @pytest.mark.asyncio
    async def test_update_order_success(self, mock_db_session, mock_order, mock_result):
        update_data = OrderUpdate(status="new status")

        updated_order = await order_crud.update(db=mock_db_session, db_obj=mock_order, obj_in=update_data)

        assert updated_order.status == "new status"

    @pytest.mark.asyncio
    async def test_delete_order_success(self, mock_db_session, mock_order, mock_result):
        mock_result.scalar_one_or_none.return_value = mock_order
        mock_db_session.execute.return_value = mock_result

        result = await order_crud.delete_by_user(db=mock_db_session, order_id=mock_order.id, user_id=mock_order.user_id)

        assert result == mock_order
        mock_db_session.delete.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_order_not_found(self, mock_db_session, mock_order, mock_result):
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await order_crud.delete_by_user(db=mock_db_session, order_id=mock_order.id, user_id=mock_order.user_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == 'Order not found'
