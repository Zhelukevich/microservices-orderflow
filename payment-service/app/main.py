from contextlib import asynccontextmanager
from typing import Annotated

from aiokafka import AIOKafkaProducer
from app.config import NotFoundError, settings
from app.database import engine
from app.dependencies import get_payment_service
from app.kafka import create_kafka_producer
from app.models import Base
from app.rabbitmq import connect_rabbitmq, declare_payment_exchange
from app.schemas import PaymentCreateSchema, PaymentReadSchema
from app.service import PaymentService
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as database_connection:
        await database_connection.run_sync(Base.metadata.create_all)

    rebbitmq_connection = await connect_rabbitmq(url=settings.rabbitmq_url)
    channel = await rebbitmq_connection.channel()
    kafka_producer: AIOKafkaProducer = create_kafka_producer()

    app.state.payment_exchange = await declare_payment_exchange(
        channel=channel,
        exchange_name=settings.payment_exchange_name,
    )
    await kafka_producer.start()
    app.state.kafka_producer = kafka_producer

    try:
        yield
    finally:
        await kafka_producer.stop()
        await rebbitmq_connection.close()


app = FastAPI(lifespan=lifespan)

PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]


@app.exception_handler(NotFoundError)
def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc) or "Resource not found"},
    )


@app.get(
    "/payments/{payment_id}",
    response_model=PaymentReadSchema,
)
async def get_payment(
    payment_id: str,
    payment_service: PaymentServiceDep,
):
    return await payment_service.get(payment_id)


@app.post(
    "/payments/",
    response_model=PaymentReadSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    payload: PaymentCreateSchema,
    request: Request,
    payment_service: PaymentServiceDep,
):
    payment = await payment_service.create(payload)

    await payment_service.complete_payment(
        payment,
        order_id=payload.order_id,
        user_id=payload.user_id,
        amount=payload.amount,
        exchange=request.app.state.payment_exchange,
        kafka_producer=request.app.state.kafka_producer,
    )

    return payment
