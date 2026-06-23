from functools import lru_cache

from pymongo import MongoClient

from app.config import Settings
from app.event_dispatcher import BrokerEventDispatcher, EventDispatcher
from app.order_repository import MongoOrderRepository, OrderRepository


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()


@lru_cache
def get_mongo_client() -> MongoClient:
    return MongoClient(get_settings().mongo_url, serverSelectionTimeoutMS=5000)


def get_order_repository() -> OrderRepository:
    settings = get_settings()
    collection = get_mongo_client()[settings.mongo_database][settings.mongo_collection]
    return MongoOrderRepository(collection)


@lru_cache
def get_event_dispatcher() -> EventDispatcher:
    settings = get_settings()
    return BrokerEventDispatcher(
        settings.rabbitmq_url,
        settings.rabbitmq_queue,
        settings.kafka_bootstrap_servers,
        settings.kafka_topic,
    )
