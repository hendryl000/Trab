import json
from threading import Lock
from typing import Protocol

import pika
from kafka import KafkaProducer


class SaidaDeEventos(Protocol):
    def espalhar_pedido_criado(self, pedido: dict) -> None: ...

    def encerrar(self) -> None: ...


class PonteRabbitKafka:
    def __init__(self, endereco_rabbit: str, fila: str, servidores_kafka: str, topico: str) -> None:
        self._endereco_rabbit = endereco_rabbit
        self._fila = fila
        self._servidores_kafka = servidores_kafka
        self._topico = topico
        self._produtor: KafkaProducer | None = None
        self._trava = Lock()

    def espalhar_pedido_criado(self, pedido: dict) -> None:
        envelope = {
            "tipo": "comercio.pedido.criado",
            "versao": 1,
            "pedido": {
                "codigo": pedido["codigo"],
                "situacao": pedido["situacao"],
                "cliente": pedido["cliente"],
                "produto": pedido["produto"],
                "quantidade": pedido["quantidade"],
            },
            "ocorrido_em": pedido["registrado_em"],
        }
        self._enfileirar_aviso(envelope)
        self._registrar_no_fluxo(envelope)

    def _enfileirar_aviso(self, envelope: dict) -> None:
        conexao = pika.BlockingConnection(pika.URLParameters(self._endereco_rabbit))
        try:
            canal = conexao.channel()
            canal.queue_declare(queue=self._fila, durable=True)
            canal.basic_publish(
                exchange="",
                routing_key=self._fila,
                body=json.dumps(envelope).encode("utf-8"),
                properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
            )
        finally:
            conexao.close()

    def _registrar_no_fluxo(self, envelope: dict) -> None:
        self._obter_produtor().send(
            self._topico,
            key=envelope["pedido"]["codigo"].encode("utf-8"),
            value=envelope,
        ).get(timeout=10)

    def _obter_produtor(self) -> KafkaProducer:
        with self._trava:
            if self._produtor is None:
                self._produtor = KafkaProducer(
                    bootstrap_servers=self._servidores_kafka,
                    value_serializer=lambda valor: json.dumps(valor).encode("utf-8"),
                )
            return self._produtor

    def encerrar(self) -> None:
        with self._trava:
            if self._produtor is not None:
                self._produtor.close()
                self._produtor = None
