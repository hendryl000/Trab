# OrderFlow API

API de gerenciamento de pedidos construída com FastAPI. Os pedidos são persistidos no MongoDB e, após o cadastro, a aplicação envia a mesma ocorrência de criação para uma fila RabbitMQ e para um tópico Kafka.

## Arquitetura

```text
Cliente -> FastAPI -> MongoDB (customer_orders)
                    -> RabbitMQ (new-order-notifications)
                    -> Kafka (order-lifecycle-events)
```

O RabbitMQ representa a entrega em fila para processamento assíncrono. O Kafka registra o evento de domínio para que diferentes sistemas possam consumi-lo. O evento contém o tipo `ORDER_CREATED`, identificador, status e dados básicos do pedido.

## Estrutura

```text
app/
├── config.py              # variáveis de ambiente
├── dependencies.py        # composição das dependências
├── event_dispatcher.py    # publicação RabbitMQ e Kafka
├── main.py                # aplicação e endpoints FastAPI
├── order_repository.py    # persistência MongoDB
└── schemas.py             # modelos e validações
tests/
└── test_orders.py
Dockerfile
docker-compose.yml
requirements.txt
```

## Executar

É necessário ter Docker e Docker Compose instalados. Na raiz do projeto, execute:

```bash
docker compose up --build
```

O único comando inicia FastAPI, MongoDB, RabbitMQ, Kafka e ZooKeeper. A API fica disponível em <http://localhost:8000> e o Swagger em <http://localhost:8000/docs>. O painel RabbitMQ fica em <http://localhost:15672> (`guest` / `guest`).

Para encerrar:

```bash
docker compose down
```

Use `docker compose down -v` somente se também desejar apagar os pedidos persistidos no volume MongoDB.

## Endpoints

### Cadastrar pedido

`POST /orders`

```json
{
  "customer_name": "Ana Souza",
  "product_name": "Teclado mecanico",
  "quantity": 2
}
```

Resposta `201 Created`:

```json
{
  "customer_name": "Ana Souza",
  "product_name": "Teclado mecanico",
  "quantity": 2,
  "id": "87cce0a7-bcf1-420e-bbb4-455b17d6733c",
  "status": "PENDENTE"
}
```

O identificador UUID e o status inicial são definidos pela API, não pelo cliente.

### Listar pedidos

`GET /orders`

Retorna todos os pedidos, dos mais recentes para os mais antigos.

### Saúde

`GET /health`

## Testes

Os testes usam implementações em memória para isolar o comportamento HTTP. Assim, validam cadastro, listagem, evento e regras de entrada sem exigir os serviços Docker:

```bash
python -m pytest -v
```

Também é possível executar os testes dentro da imagem da aplicação:

```bash
docker compose run --rm api pytest -v
```

## Decisões de implementação

- UUID evita dependência do `_id` interno do MongoDB.
- A coleção utilizada é `customer_orders`, separada para o recurso.
- Mensagens RabbitMQ são duráveis e persistentes.
- O envio Kafka aguarda confirmação do broker.
- Repositório e publicador seguem contratos substituíveis, facilitando testes e manutenção.
