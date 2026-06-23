from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Depends, FastAPI, status

from app.acervo_pedidos import AcervoDePedidos
from app.contratos import PedidoCadastrado, PedidoParaCadastrar, SituacaoPedido
from app.montagem import acervo_pedidos, cliente_mongo, saida_eventos
from app.ponte_eventos import SaidaDeEventos


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    yield
    saida_eventos().encerrar()
    cliente_mongo().close()


app = FastAPI(
    title="RastroPedido API",
    description="Registro de pedidos e propagacao de acontecimentos comerciais.",
    version="1.0.0",
    lifespan=ciclo_de_vida,
)


@app.get("/", tags=["Operacao"])
def inicio() -> dict[str, str]:
    return {"servico": "RastroPedido API", "documentacao": "/docs"}


@app.get("/saude", tags=["Operacao"])
def verificar_saude() -> dict[str, str]:
    return {"situacao": "disponivel"}


@app.post(
    "/pedidos",
    response_model=PedidoCadastrado,
    status_code=status.HTTP_201_CREATED,
    tags=["Pedidos"],
)
def cadastrar_pedido(
    entrada: PedidoParaCadastrar,
    acervo: AcervoDePedidos = Depends(acervo_pedidos),
    eventos: SaidaDeEventos = Depends(saida_eventos),
) -> dict:
    pedido = {
        "codigo": str(uuid4()),
        **entrada.model_dump(),
        "situacao": SituacaoPedido.PENDENTE.value,
        "registrado_em": datetime.now(timezone.utc).isoformat(),
    }
    acervo.guardar(pedido)
    eventos.espalhar_pedido_criado(pedido)
    return pedido


@app.get("/pedidos", response_model=list[PedidoCadastrado], tags=["Pedidos"])
def listar_pedidos(acervo: AcervoDePedidos = Depends(acervo_pedidos)) -> list[dict]:
    return acervo.consultar_todos()
