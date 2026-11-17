from contextlib import asynccontextmanager

# from app.config import settings
from app.database import engine
from app.models import Base
from app.schemas import OrderCreateSchema, OrderReadSchema
from app.service import OrderService
from fastapi import Depends, FastAPI


@asynccontextmanager
async def lifespan(_: FastAPI):

    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI()


@app.get(
    "/order/{order_id}",
    response_model=OrderReadSchema,
)
def get_order(
    order_id,
    order_service: OrderService = Depends(get_order_service),
):
    return order_service.get(order_id)


@app.post(
    "/order/",
    response_model=OrderReadSchema,
)
def create_order(
    payload: OrderCreateSchema,
    order_service: OrderService = Depends(get_order_service),
):
    return order_service.create(payload)
