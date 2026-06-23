from fastapi.testclient import TestClient

from app.dependencies import get_event_dispatcher, get_order_repository
from app.main import app


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self.orders: list[dict] = []

    def add(self, order: dict) -> dict:
        self.orders.append(order.copy())
        return order

    def find_all(self) -> list[dict]:
        return list(reversed(self.orders))


class EventSpy:
    def __init__(self) -> None:
        self.created_orders: list[dict] = []

    def announce_created(self, order: dict) -> None:
        self.created_orders.append(order.copy())

    def close(self) -> None:
        pass


repository = InMemoryOrderRepository()
events = EventSpy()
app.dependency_overrides[get_order_repository] = lambda: repository
app.dependency_overrides[get_event_dispatcher] = lambda: events
client = TestClient(app)


def setup_function() -> None:
    repository.orders.clear()
    events.created_orders.clear()


def test_create_order_stores_data_and_dispatches_event() -> None:
    response = client.post(
        "/orders",
        json={"customer_name": "Marina Lima", "product_name": "Monitor 27", "quantity": 1},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["status"] == "PENDENTE"
    assert body["customer_name"] == "Marina Lima"
    assert repository.orders[0]["id"] == body["id"]
    assert events.created_orders[0]["id"] == body["id"]


def test_list_orders_returns_registered_orders() -> None:
    first = client.post(
        "/orders",
        json={"customer_name": "Caio Nunes", "product_name": "Mouse", "quantity": 2},
    )
    second = client.post(
        "/orders",
        json={"customer_name": "Lia Alves", "product_name": "Webcam", "quantity": 1},
    )

    response = client.get("/orders")

    assert first.status_code == 201
    assert second.status_code == 201
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["customer_name"] == "Lia Alves"


def test_rejects_non_positive_quantity() -> None:
    response = client.post(
        "/orders",
        json={"customer_name": "Joao Silva", "product_name": "Cabo USB", "quantity": 0},
    )

    assert response.status_code == 422
