from enum import Enum

from pydantic import BaseModel, Field


class SituacaoPedido(str, Enum):
    PENDENTE = "PENDENTE"


class PedidoParaCadastrar(BaseModel):
    cliente: str = Field(min_length=2, max_length=120, examples=["Ana Souza"])
    produto: str = Field(min_length=2, max_length=160, examples=["Teclado mecanico"])
    quantidade: int = Field(gt=0, examples=[2])


class PedidoCadastrado(PedidoParaCadastrar):
    codigo: str
    situacao: SituacaoPedido
