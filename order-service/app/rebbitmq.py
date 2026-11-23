import json

import aio_pika
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractIncomingMessage,
    AbstractQueue,
    AbstractRobustConnection,
    ExchangeType,
)
from app.config import settings
from app.database import SessionLocal
from app.models import Order


async def connect_rabbitmq() -> AbstractRobustConnection:
    return await aio_pika.connect_robust(settings.rabbitmq_url)


async def handle_payment_events(message: AbstractIncomingMessage) -> None:
    async with message.process(requeue=False):
        event = json.loads(message.body.decode("utf-8"))
        with SessionLocal() as session:
            order = session.get(Order, event["order_id"])

            if order is None:
                print(f"Order {event.get('order_id')} not found")
                return

            order.status = "paid"
            session.commit()
            print("Статус успешно обновлен")


async def start_payment_consumer(
    connection: AbstractConnection,
) -> AbstractQueue:
    channel: AbstractChannel = await connection.channel()

    payment_exchange = await channel.declare_exchange(
        name=settings.payment_exchange_name,
        type=ExchangeType.DIRECT,
        durable=True,
    )

    payment_queue = await channel.declare_queue(
        name=settings.payment_queue_name,
        durable=True,
    )

    await payment_queue.bind(
        exchange=payment_exchange,
        routing_key=settings.payment_succeeded_routing_key,
    )

    await payment_queue.consume(handle_payment_events)

    return payment_queue
