from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreateSchema(BaseModel):
    quantity: int = Field(gt=0)
    unit_price: int = Field(ge=0)


class OrderItemReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    product_name: str
    quantity: int
    unit_price: int


class OrderCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    items: list[OrderItemCreateSchema]


class OrderReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: int
    status: str
    total_amount: int
    items: list[OrderItemReadSchema]
