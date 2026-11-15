from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse)
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix = "/api/auth", tags = ["Auth"])

# API đăng kí tài khoản
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    # Kiểm tra xem email đã tồn tại chưa
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "This email has aldready been used."
        )

    # Băm mật khẩu từ request
    hashed_password_register = hash_password(payload.password)

    # Tạo object user mới cho vào database
    new_user = User(
        email = payload.email,
        full_name = payload.full_name,
        hashed_password = hashed_password_register
    )
    # Cho vào database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "You have registered successfully!",
        "user_id": new_user.id,
        "email": new_user.email,
        "full_name": new_user.full_name,
    }

# API đăng nhập
@router.post("/login", response_model = TokenResponse)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    # Tìm user theo email
    user = db.query(User).filter(User.email == payload.email).first()

    # Kiểm tra mật khẩu nhập
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password.",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    # Tạo access token
    access_token = create_access_token(subject = user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
    }

# API kiểm tra user có đang đăng nhập
@router.get("/me", response_model = UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
