# Pydantic models
from datetime import datetime
from pydantic import BaseModel, Field


class RegisterUserRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    password: str = Field(
        ..., min_length=3, description="Password must be at least 3 characters"
    )


class LoginRequest(BaseModel):
    first_name: str = Field(..., min_length=1)
    password: str = Field(...)


class PrayerLogRequest(BaseModel):
    user_id: int
    morning: int = Field(default=0, ge=0)
    afternoon: int = Field(default=0, ge=0)
    night: int = Field(default=0, ge=0)

    class Config:
        orm_mode = True
