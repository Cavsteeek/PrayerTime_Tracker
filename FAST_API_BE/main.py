from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import Date
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from schemas import LoginRequest, PrayerLogRequest, RegisterUserRequest
from database import Base, engine, get_db
from models import User, PrayerLog
from auth import hash_password, create_access_token, verify_password
from datetime import datetime

app = FastAPI()

# Initialize database
Base.metadata.create_all(bind=engine)


# Endpoints
@app.post("/register")
def register_user(post: RegisterUserRequest, db: Session = Depends(get_db)):
    hashed_password = hash_password(post.password)
    user = User(
        first_name=post.first_name,
        last_name=post.last_name,
        password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully"}


@app.post("/login")
def login_user(post: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.first_name == post.first_name).first()
    if not user or not verify_password(post.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token}


@app.post("/prayer-log")
def log_prayer(post: PrayerLogRequest, db: Session = Depends(get_db)):
    # Use the current date if `date` is not provided in the post
    log = PrayerLog(
        user_id=post.user_id,
        morning=post.morning,
        afternoon=post.afternoon,
        night=post.night,
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
