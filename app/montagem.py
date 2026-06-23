from functools import lru_cache

from pymongo import MongoClient

from app.acervo_pedidos import AcervoDePedidos, AcervoMongo
from app.config import Settings
from app.ponte_eventos import PonteRabbitKafka, SaidaDeEventos


@lru_cache
def configuracao() -> Settings:
    return Settings.from_env()


@lru_cache
def cliente_mongo() -> MongoClient:
    return MongoClient(configuracao().mongo_url, serverSelectionTimeoutMS=5000)


def acervo_pedidos() -> AcervoDePedidos:
    ajustes = configuracao()
    colecao = cliente_mongo()[ajustes.mongo_database][ajustes.mongo_collection]
    return AcervoMongo(colecao)


@lru_cache
def saida_eventos() -> SaidaDeEventos:
    ajustes = configuracao()
    return PonteRabbitKafka(
        ajustes.rabbitmq_url,
        ajustes.rabbitmq_queue,
        ajustes.kafka_bootstrap_servers,
        ajustes.kafka_topic,
    )
