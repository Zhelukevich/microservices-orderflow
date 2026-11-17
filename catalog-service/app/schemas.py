from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    price: str
    image: str
    catalog: str


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    price: str
    image: str
    catalog: str
