from app.kafka.producer import KafkaOrderProducer
from app.schemas.order_event import EventMetadata, OrderEvent
from app.schemas.orders import OrderDB

producer = KafkaOrderProducer(bootstrap_servers='kafka:29092')


def send_order_created_event(order: OrderDB):
    metadata = EventMetadata(event_type="order.created")
    event = OrderEvent(metadata=metadata, data=order)

    return producer.send_order_event(event=event, topic="ORDER_CREATED", key=str(order.id))


def send_order_updated_event(order: OrderDB):
    metadata = EventMetadata(event_type="order.updated")
    event = OrderEvent(metadata=metadata, data=order)

    return producer.send_order_event(event=event, topic="ORDER_UPDATED", key=str(order.id))
