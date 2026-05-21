import logging
from typing import Optional

from confluent_kafka import Producer

from app.schemas.order_event import OrderEvent

logger = logging.getLogger(__name__)


class KafkaOrderProducer:
    def __init__(self, bootstrap_servers: str = "kafka:29092"):
        self.config = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": "orders-service",
            "acks": "all",
            "enable.idempotence": True,
            "max.in.flight.requests.per.connection": 5,
            "retries": 3,
            "retry.backoff.ms": 1000,
            "batch.size": 16384,
            "linger.ms": 10,
            "compression.type": "snappy",
            "request.timeout.ms": 3000,
            "delivery.timeout.ms": 5000,
        }
        self.producer = Producer(self.config)

    def delivery_callback(self, err, msg):
        if err:
            logger.warning("Failed to deliver message", extra={"error": err})
        else:
            logger.info("Message delivered", extra={"topic": msg.topic(), "partition": msg.partition()})

    def send_order_event(self, event: OrderEvent,
                         topic: str,
                         key: Optional[str] = None,
                         headers: Optional[dict[str, str]] = None) -> bool:
        try:
            value = event.model_dump_json().encode("utf-8")
            key = key or str(event.data.id)
            key_bytes = key.encode("utf-8")

            self.producer.produce(topic=topic, key=key_bytes, value=value, headers=headers,
                                  callback=self.delivery_callback)
            self.producer.poll(0)

            logger.info("Message sent", extra={"topic": topic})
            return True

        except BufferError:
            logger.warning("Message failed to send: queue is full", extra={"topic": topic})
            self.producer.poll(1)
            return self.send_order_event(event, topic, key, headers)

        except Exception as e:
            logger.exception("Failed to send message", extra={
                "topic": topic,
                "error_type": type(e).__name__
            })
            return False

    def close(self):
        self.producer.flush()
        self.producer.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
