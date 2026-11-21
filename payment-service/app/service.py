import asyncio

from app.config import NotFoundError
from app.models import PaymentORM
from schemas import PaymentCreateSchema, PaymentReadSchema
from sqlalchemy.ext.asyncio import AsyncSession


class PaymentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payment_data: PaymentCreateSchema) -> PaymentReadSchema:
        payment = PaymentORM(
            order_id=payment_data.order_id,
            status="created",
            amount=payment_data.amount,
        )
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return PaymentReadSchema.model_validate(payment)

    async def get(self, payment_id: str):
        payment = await self.session.get(PaymentORM, payment_id)
        if payment is None:
            raise NotFoundError()

        return payment

    async def complete_payment(self, payment: PaymentORM):
        await asyncio.sleep(4)

        payment.status = "succeeded"
        await self.session.commit()

        await publish_payment_completed_event()
