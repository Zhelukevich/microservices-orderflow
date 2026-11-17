from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import engine, get_db
from app.models import Base, Product
from app.schemas import ProductCreate, ProductRead
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(_: FastAPI):

    Base.metadata.create_all(bind=engine)
    yield


settings = get_settings()
app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=setattr.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("products", response_model=list[ProductRead])
def get_products(
    db: Session = Depends(get_db),
):
    query = select(Product).order_by(Product.name)
    return list(db.scalars(query).all())


@app.get("products/{products_id}", response_model=ProductRead)
def get_product(
    product_id: str,
    db: Session = Depends(get_db),
) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )
    return product


@app.post(
    "products",
    response_model=ProductCreate,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
