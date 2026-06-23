from typing import Protocol

from pymongo.collection import Collection


class AcervoDePedidos(Protocol):
    def guardar(self, pedido: dict) -> None: ...

    def consultar_todos(self) -> list[dict]: ...


class AcervoMongo:
    def __init__(self, colecao: Collection) -> None:
        self._colecao = colecao

    def guardar(self, pedido: dict) -> None:
        self._colecao.insert_one(pedido.copy())

    def consultar_todos(self) -> list[dict]:
        consulta = self._colecao.find({}, {"_id": 0}).sort("registrado_em", -1)
        return list(consulta)
