from enum import Enum


class OrderStatus(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    RECEIVED = 'received'
    CANCELED = 'canceled'
