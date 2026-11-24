from app.database import get_db
from app.models import User
from app.schemas import TokenResponse, UserLogin, UserRead, UserRegister
from app.security import create_access_token, hash_password, verify_password
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

app = FastAPI()


@app.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserRegister,
    db: Session = Depends(get_db),
):
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()

    access_token = create_access_token(user)

    return TokenResponse(
        access_token=access_token,
        user=UserRead.model_validate(user),
    )


DUMMY_HASH = hash_password("dummy-password-for-timing-protection")


@app.post("/login", response_model=TokenResponse)
def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))

    if user is None:
        verify_password(payload.password, DUMMY_HASH)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user)

    return TokenResponse(
        access_token=access_token,
        user=UserRead.model_validate(user),
    )
