from decimal import Decimal

from app.schemas.orders import OrderItemBase


def get_cart_price(items: list[OrderItemBase]):
    cart_price = Decimal(0)

    for item in items:
        cart_price += item.unit_price * item.quantity

    return cart_price


def get_delivery_price() -> Decimal:
    return Decimal(5)


def get_total_price(cart_price: Decimal, delivery_price: Decimal) -> Decimal:
    return cart_price + delivery_price
