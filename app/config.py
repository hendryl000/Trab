import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    mongo_url: str
    mongo_database: str
    mongo_collection: str
    kafka_bootstrap_servers: str
    kafka_topic: str
    rabbitmq_url: str
    rabbitmq_queue: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            mongo_url=os.getenv("MONGO_URL", "mongodb://localhost:27017"),
            mongo_database=os.getenv("MONGO_DATABASE", "order_hub"),
            mongo_collection=os.getenv("MONGO_COLLECTION", "customer_orders"),
            kafka_bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094"),
            kafka_topic=os.getenv("KAFKA_TOPIC", "order-lifecycle-events"),
            rabbitmq_url=os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F"),
            rabbitmq_queue=os.getenv("RABBITMQ_QUEUE", "new-order-notifications"),
        )
