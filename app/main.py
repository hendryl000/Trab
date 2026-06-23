from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Depends, FastAPI, status

from app.dependencies import get_event_dispatcher, get_mongo_client, get_order_repository
from app.event_dispatcher import EventDispatcher
from app.order_repository import OrderRepository
from app.schemas import OrderCreate, OrderStatus, OrderView


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    get_event_dispatcher().close()
    get_mongo_client().close()


app = FastAPI(
    title="OrderFlow API",
    description="Gerenciamento de pedidos com MongoDB e eventos assincronos.",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Sistema"])
def root() -> dict[str, str]:
    return {"service": "OrderFlow API", "documentation": "/docs"}


@app.get("/health", tags=["Sistema"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/orders", response_model=OrderView, status_code=status.HTTP_201_CREATED, tags=["Pedidos"])
def create_order(
    payload: OrderCreate,
    repository: OrderRepository = Depends(get_order_repository),
    dispatcher: EventDispatcher = Depends(get_event_dispatcher),
) -> dict:
    order = {
        "id": str(uuid4()),
        **payload.model_dump(),
        "status": OrderStatus.PENDING.value,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    repository.add(order)
    dispatcher.announce_created(order)
    return order


@app.get("/orders", response_model=list[OrderView], tags=["Pedidos"])
def list_orders(repository: OrderRepository = Depends(get_order_repository)) -> list[dict]:
    return repository.find_all()
