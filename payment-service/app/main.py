import time
from contextlib import asynccontextmanager
from typing import Annotated

from app.config import NotFoundError
from app.database import engine
from app.dependencies import get_payment_service
from app.models import Base
from app.schemas import PaymentCreateSchema
from app.service import PaymentService
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]


@app.exception_handler(NotFoundError)
def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc) or "Resource not found"},
    )


@app.get(
    "/payments/{payments_id}",
    response_model=PaymentCreateSchema,
)
async def get_payment(
    payment_id: str,
    payment_service: PaymentServiceDep,
):
    return await payment_service.get(payment_id)


@app.post(
    "/payments/",
    response_model=PaymentCreateSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    payload: PaymentCreateSchema,
    payment_service: PaymentServiceDep,
):
    payment = await payment_service.create(payload)
    time.sleep(3)

    await payment_service.complete_payment(payment)
