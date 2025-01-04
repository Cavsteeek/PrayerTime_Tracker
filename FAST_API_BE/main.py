from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import Date
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from database import Base, engine, get_db
from models import User, PrayerLog
from auth import hash_password, create_access_token, verify_password
from datetime import date

app = FastAPI()

# Initialize database
Base.metadata.create_all(bind=engine)


# Pydantic models
class RegisterUserRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    password: str = Field(
        ..., min_length=6, description="Password must be at least 6 characters"
    )


class LoginRequest(BaseModel):
    first_name: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)


class PrayerLogRequest(BaseModel):
    user_id: int
    morning: int = Field(default=0, ge=0)
    afternoon: int = Field(default=0, ge=0)
    night: int = Field(default=0, ge=0)


# Endpoints
@app.post("/register")
def register_user(payload: RegisterUserRequest, db: Session = Depends(get_db)):
    hashed_password = hash_password(payload.password)
    user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully"}


@app.post("/login")
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.first_name == payload.first_name).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token}


@app.post("/prayer-log")
def log_prayer(payload: PrayerLogRequest, db: Session = Depends(get_db)):
    # Use the current date if `date` is not provided in the payload
    log = PrayerLog(
        user_id=payload.user_id,
        morning=payload.morning,
        afternoon=payload.afternoon,
        night=payload.night,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {
        "message": "Prayer log added successfully",
        "log_date": log.date,
        "total_time_hr_min": log.total_time_hr_min,
    }


@app.get("/prayer-summary/{user_id}")
def get_weekly_prayer_summary(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(PrayerLog).filter(PrayerLog.user_id == user_id).all()
    weekly_summary = {log.date: log.total_time_hr_min for log in logs}
    total_time = sum(log.total_time for log in logs)
    return {
        "weekly_summary": weekly_summary,
        "total_time_hr_min": f"{total_time // 60} hr {total_time % 60} min",
    }
