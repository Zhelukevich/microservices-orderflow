import asyncio

from aio_pika.abc import AbstractExchange
from aiokafka import AIOKafkaProducer
from app.config import NotFoundError, settings
from app.events import build_payment_succeeded_event
from app.kafka import publish_kafka_event
from app.models import PaymentORM
from app.rabbitmq import event_publish_json
from app.schemas import PaymentCreateSchema
from sqlalchemy.ext.asyncio import AsyncSession


class PaymentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payment_data: PaymentCreateSchema) -> PaymentORM:
        payment = PaymentORM(
            order_id=payment_data.order_id,
            user_id=payment_data.user_id,
            status="created",
            amount=payment_data.amount,
        )
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment

    async def get(self, payment_id: str) -> PaymentORM:
        payment = await self.session.get(PaymentORM, payment_id)
        if payment is None:
            raise NotFoundError(f"Payment {payment_id} not found")
        return payment

    async def complete_payment(
        self,
        payment: PaymentORM,
        user_id: int,
        order_id: str,
        amount: int,
        exchange: AbstractExchange,
        kafka_producer: AIOKafkaProducer,
    ) -> PaymentCreateSchema:
        await asyncio.sleep(4)

        payment.status = "succeeded"
        await self.session.commit()

        event = build_payment_succeeded_event(
            amount=amount,
            payment_id=payment.id,
            order_id=order_id,
            user_id=str(user_id),
        )

        await event_publish_json(
            exchange=exchange,
            data=event,
            routing_key=settings.payment_succeeded_routing_key,
        )

        await publish_kafka_event(
            producer=kafka_producer,
            event=event,
            topic=settings.kafka_analytic_payment_topic,
        )

        return PaymentCreateSchema.model_validate(payment)
