from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(str, Enum):
    PENDING = "PENDENTE"


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=120, examples=["Ana Souza"])
    product_name: str = Field(min_length=2, max_length=160, examples=["Teclado mecanico"])
    quantity: int = Field(gt=0, examples=[2])


class OrderView(OrderCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: OrderStatus
