# app/schemas.py

from pydantic import BaseModel, EmailStr, constr, validator
import datetime

class UserCreate(BaseModel):
    """
    Schema for user signup requests.
    """
    email: EmailStr
    password: constr(min_length=8)

    @validator('password')
    def password_complexity(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

class UserLogin(BaseModel):
    """
    Schema for user login requests.
    """
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """
    Schema for user response data.
    """
    email: EmailStr
    token: str

class PostCreate(BaseModel):
    """
    Schema for creating a new post.
    """
    text: str

    @validator('text')
    def validate_text_size(cls, v):
        if len(v.encode('utf-8')) > 1_048_576:  # 1 MB in bytes
            raise ValueError("Post text exceeds maximum allowed size of 1 MB")
        return v

class PostResponse(BaseModel):
    """
    Schema for post response data.
    """
    id: int
    text: str
    created_at: datetime.datetime
    user_id: int
