from sqlalchemy import Column, String, Boolean, DateTime, Date, Text, Integer
from src.backend_services.account.database.database import Base
from datetime import datetime, UTC

from src.backend_services.account.database.enum_statuses import USER_STATUS


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(36), unique=True, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)

    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)

    gender = Column(String(20), nullable=True)
    date_of_birth = Column(Date, default=lambda: datetime.now(UTC), nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    email_verified = Column(Boolean, default=False, nullable=False)
    user_status = Column(USER_STATUS, default='Unverified', nullable=False)
