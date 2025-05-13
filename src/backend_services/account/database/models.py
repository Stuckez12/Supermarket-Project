from datetime import datetime, UTC
from sqlalchemy import Column, String, Boolean, DateTime, Date, Text, Integer

from src.backend_services.account.database.db_enum_statuses import USER_STATUS_ENUM, GENDER_ENUM, ROLE_ENUM
from src.backend_services.account.database.database import Base


class User(Base):
    '''
    The table for all users/customers of the application.
    It contains all the required data and columns to record the activity of the user.
    '''

    __tablename__ = "user"

    # Unique Column Identifiers
    id = Column(Integer, primary_key=True, nullable=False) # System Use Only
    uuid = Column(String(36), unique=True, nullable=False) # Public Use Accessible
    email = Column(Text, unique=True, nullable=False)                                   # User Input

    # Accounts' Password Management
    password = Column(Text, nullable=False)                                             # User Input
    password_last_changed_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(DateTime, nullable=True)

    # Generic User Details
    first_name = Column(Text, nullable=False)                                           # User Input
    last_name = Column(Text, default='Other', nullable=False)                           # User Input
    gender = Column(GENDER_ENUM, nullable=False)                                        # User Input
    date_of_birth = Column(Date, default=lambda: datetime.now(UTC), nullable=False)     # User Input

    # Account Activity Recorded
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    last_login = Column(DateTime, default=lambda: datetime.now(UTC), nullable=True)
    last_activity_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=True)

    # Account Statuses
    email_verified = Column(Boolean, default=False, nullable=False)
    user_status = Column(USER_STATUS_ENUM, default='Unverified', nullable=False)
    user_role = Column(ROLE_ENUM, default='Customer', nullable=False)


    def is_accessible(self):
        return self.role.in_(['Active', 'Inactive', 'Unverified'])
    

    def is_logged_in(self):
        return self.role.in_(['Active'])
