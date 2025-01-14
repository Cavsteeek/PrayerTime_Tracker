from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import text
from database import Base
from sqlalchemy.sql.sqltypes import TIMESTAMP


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    password = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class PrayerLog(Base):
    __tablename__ = "prayer_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    date = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    morning = Column(Integer, default=0)
    afternoon = Column(Integer, default=0)
    night = Column(Integer, default=0)

    @property
    def total_time(self):
        return self.morning + self.afternoon + self.night

    @property
    def total_time_hr_min(self):
        total_minutes = self.total_time
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours} hr {minutes} min"
