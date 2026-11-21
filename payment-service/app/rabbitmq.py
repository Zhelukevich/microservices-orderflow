import json

import aio_pika
from aio_pika.abc import (
    AbstractChannel,
    AbstractExchange,
    AbstractRobustConnection,
    ExchangeType,
)


async def connect_rabbitmq(url: str) -> AbstractRobustConnection:
    return await aio_pika.connect_robust(url)


async def declare_payment_exchange(
    channel: AbstractChannel, exchange_name: str
) -> AbstractExchange:
    return await channel.declare_exchange(
        name=exchange_name,
        type=ExchangeType.DIRECT,
        durable=True,
    )


async def publish_json(
    exchange: AbstractExchange, routing_key: str, data: dict
) -> None:
    message = aio_pika.Message(
        body=json.dumps(data).encode("utf-8"),
        content_type="application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )
    await exchange.publish(message=message, routing_key=routing_key)
