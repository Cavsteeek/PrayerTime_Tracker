from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User, PrayerLog
from auth import hash_password, create_access_token, verify_password

app = FastAPI()

# Initialize database
Base.metadata.create_all(bind=engine)


@app.post("/register")
def register_user(
    first_name: str, last_name: str, password: str, db: Session = Depends(get_db)
):
    hashed_password = hash_password(password)
    user = User(first_name=first_name, last_name=last_name, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully"}


@app.post("/login")
def login_user(first_name: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.first_name == first_name).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token}


@app.post("/prayer-log")
def log_prayer(
    user_id: int,
    date: str,
    morning: int = 0,
    afternoon: int = 0,
    night: int = 0,
    db: Session = Depends(get_db),
):
    log = PrayerLog(
        user_id=user_id, date=date, morning=morning, afternoon=afternoon, night=night
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"message": "Prayer log added successfully"}


@app.get("/prayer-summary/{user_id}")
def get_weekly_prayer_summary(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(PrayerLog).filter(PrayerLog.user_id == user_id).all()
    weekly_summary = {log.date: log.total_time_hr_min for log in logs}
    total_time = sum(log.total_time for log in logs)
    return {
        "weekly_summary": weekly_summary,
        "total_time_hr_min": f"{total_time // 60} hr {total_time % 60} min",
    }
