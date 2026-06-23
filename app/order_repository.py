from typing import Protocol

from pymongo.collection import Collection


class OrderRepository(Protocol):
    def add(self, order: dict) -> dict: ...

    def find_all(self) -> list[dict]: ...


class MongoOrderRepository:
    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def add(self, order: dict) -> dict:
        self._collection.insert_one(order.copy())
        return order

    def find_all(self) -> list[dict]:
        return list(self._collection.find({}, {"_id": 0}).sort("created_at", -1))
