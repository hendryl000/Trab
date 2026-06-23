from fastapi.testclient import TestClient

from app.main import app
from app.montagem import acervo_pedidos, saida_eventos


class AcervoEmMemoria:
    def __init__(self) -> None:
        self.itens: list[dict] = []

    def guardar(self, pedido: dict) -> None:
        self.itens.append(pedido.copy())

    def consultar_todos(self) -> list[dict]:
        return list(reversed(self.itens))


class EspiaoDeEventos:
    def __init__(self) -> None:
        self.pedidos_espalhados: list[dict] = []

    def espalhar_pedido_criado(self, pedido: dict) -> None:
        self.pedidos_espalhados.append(pedido.copy())

    def encerrar(self) -> None:
        pass


acervo = AcervoEmMemoria()
espiao = EspiaoDeEventos()
app.dependency_overrides[acervo_pedidos] = lambda: acervo
app.dependency_overrides[saida_eventos] = lambda: espiao
cliente = TestClient(app)


def setup_function() -> None:
    acervo.itens.clear()
    espiao.pedidos_espalhados.clear()


def test_cadastro_guarda_pedido_e_espalha_acontecimento() -> None:
    resposta = cliente.post(
        "/pedidos",
        json={"cliente": "Marina Lima", "produto": "Monitor 27", "quantidade": 1},
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["codigo"]
    assert corpo["situacao"] == "PENDENTE"
    assert corpo["cliente"] == "Marina Lima"
    assert acervo.itens[0]["codigo"] == corpo["codigo"]
    assert espiao.pedidos_espalhados[0]["codigo"] == corpo["codigo"]


def test_consulta_apresenta_pedidos_mais_recentes_primeiro() -> None:
    primeira = cliente.post(
        "/pedidos",
        json={"cliente": "Caio Nunes", "produto": "Mouse", "quantidade": 2},
    )
    segunda = cliente.post(
        "/pedidos",
        json={"cliente": "Lia Alves", "produto": "Webcam", "quantidade": 1},
    )

    resposta = cliente.get("/pedidos")

    assert primeira.status_code == 201
    assert segunda.status_code == 201
    assert resposta.status_code == 200
    assert len(resposta.json()) == 2
    assert resposta.json()[0]["cliente"] == "Lia Alves"


def test_quantidade_precisa_ser_positiva() -> None:
    resposta = cliente.post(
        "/pedidos",
        json={"cliente": "Joao Silva", "produto": "Cabo USB", "quantidade": 0},
    )

    assert resposta.status_code == 422
