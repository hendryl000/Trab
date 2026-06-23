import json
from threading import Lock
from typing import Protocol

import pika
from kafka import KafkaProducer


class EventDispatcher(Protocol):
    def announce_created(self, order: dict) -> None: ...

    def close(self) -> None: ...


class BrokerEventDispatcher:
    def __init__(self, rabbitmq_url: str, rabbitmq_queue: str, kafka_servers: str, kafka_topic: str) -> None:
        self._rabbitmq_url = rabbitmq_url
        self._rabbitmq_queue = rabbitmq_queue
        self._kafka_servers = kafka_servers
        self._kafka_topic = kafka_topic
        self._kafka_producer: KafkaProducer | None = None
        self._producer_lock = Lock()

    def announce_created(self, order: dict) -> None:
        event = {
            "event": "ORDER_CREATED",
            "order_id": order["id"],
            "status": order["status"],
            "customer_name": order["customer_name"],
            "product_name": order["product_name"],
            "quantity": order["quantity"],
            "occurred_at": order["created_at"],
        }
        self._publish_rabbitmq(event)
        self._publish_kafka(event)

    def _publish_rabbitmq(self, event: dict) -> None:
        connection = pika.BlockingConnection(pika.URLParameters(self._rabbitmq_url))
        try:
            channel = connection.channel()
            channel.queue_declare(queue=self._rabbitmq_queue, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=self._rabbitmq_queue,
                body=json.dumps(event).encode("utf-8"),
                properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
            )
        finally:
            connection.close()

    def _publish_kafka(self, event: dict) -> None:
        self._get_kafka_producer().send(self._kafka_topic, value=event).get(timeout=10)

    def _get_kafka_producer(self) -> KafkaProducer:
        with self._producer_lock:
            if self._kafka_producer is None:
                self._kafka_producer = KafkaProducer(
                    bootstrap_servers=self._kafka_servers,
                    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
                )
            return self._kafka_producer

    def close(self) -> None:
        with self._producer_lock:
            if self._kafka_producer is not None:
                self._kafka_producer.close()
                self._kafka_producer = None
