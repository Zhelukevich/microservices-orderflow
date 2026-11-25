from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CredentialsBase(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRegister(CredentialsBase):
    pass


class UserLogin(CredentialsBase):
    pass


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    items: list[OrderItemCreate] = Field(min_length=1)
