from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# Dữ liệu client gửi lên khi đăng ký
class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(..., description = "User email must be in a valid format")
    password: str = Field(..., min_length = 8, max_length = 64, description = "Password must be between 8 and 64 characters")
    full_name: str = Field(..., min_length = 3, max_length = 100, description = "Display full name")

# Dữ liệu client gửi lên khi đăng nhập
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

# Dữ liệu backend trả về khi đăng nhập thành công
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str

# Thông tin của người dùng cần hiển thị
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True
