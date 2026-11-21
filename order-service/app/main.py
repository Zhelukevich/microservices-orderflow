from contextlib import asynccontextmanager
from typing import Annotated

from app.config import NotFoundError
from app.database import engine
from app.dependencies import get_order_service
from app.models import Base
from app.schemas import OrderCreateSchema, OrderReadSchema
from app.service import OrderService
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]


@app.exception_handler(NotFoundError)
def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc) or "Resource not found"},
    )


@app.get(
    "/order/{order_id}",
    response_model=OrderReadSchema,
)
def get_order(
    order_id: str,
    order_service: OrderServiceDep,
):
    return order_service.get(order_id)


@app.post(
    "/order/",
    response_model=OrderReadSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    payload: OrderCreateSchema,
    order_service: OrderServiceDep,
):
    return order_service.create(payload)
