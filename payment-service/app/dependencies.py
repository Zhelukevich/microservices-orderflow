from typing import Annotated

from app.database import get_db
from app.service import PaymentService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_payment_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PaymentService:
    return PaymentService(db)
