'''
The tables required for the account-service to operate
'''

from datetime import datetime, timezone, UTC
from sqlalchemy import Column, String, Boolean, Date, Text, Integer, ForeignKey
from typing import Self

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
    password_last_changed_at = Column(Integer, default=lambda: datetime.now(timezone.utc).timestamp(), nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(Integer, default=0, nullable=True)

    # Generic User Details
    first_name = Column(Text, nullable=False)                                           # User Input
    last_name = Column(Text, default='Other', nullable=False)                           # User Input
    gender = Column(GENDER_ENUM, nullable=False)                                        # User Input
    date_of_birth = Column(Date, default=lambda: datetime.now(UTC), nullable=False)     # User Input

    # Account Activity Recorded
    created_at = Column(Integer, default=lambda: datetime.now(timezone.utc).timestamp(), nullable=False)
    updated_at = Column(Integer, default=lambda: datetime.now(timezone.utc).timestamp(), nullable=False)
    last_login = Column(Integer, default=lambda: datetime.now(timezone.utc).timestamp(), nullable=True)
    last_activity_at = Column(Integer, default=lambda: datetime.now(timezone.utc).timestamp(), nullable=True)
    last_recorded_login = Column(Integer, default=lambda: datetime.now(timezone.utc).timestamp(), nullable=True)

    # Account Statuses
    email_verified = Column(Boolean, default=False, nullable=False)
    user_status = Column(USER_STATUS_ENUM, default='Unverified', nullable=False)
    user_role = Column(ROLE_ENUM, default='Customer', nullable=False)


    def is_accessible(cls: Self) -> bool:
        '''
        Checks whether an account is accessible by the user.

        cls (Self): the sqlalchemy table class

        return (bool): account accessible flag
        '''

        return cls.user_status in ['Active', 'Inactive', 'Unverified']


    def is_verified(cls: Self) -> bool:
        '''
        Checks whether an account is verified

        cls (Self): the sqlalchemy table class

        return (bool): account verified flag
        '''

        return cls.email_verified


    def is_logged_in(cls: Self) -> bool:
        '''
        Checks whether an account is already in use

        cls (Self): the sqlalchemy table class

        return (bool): account logged in flag
        '''

        return cls.user_status in ['Active']


class UserLoginAttempts(Base):
    '''
    The table for all failed login attempts related to an account within the application.
    '''

    __tablename__ = "user_login_attempts"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(ForeignKey('user.id'))
    failed_datetime = Column(Integer, default=lambda: datetime.now(timezone.utc).timestamp(), nullable=False)
    expires = Column(Integer, default=lambda: datetime.now(timezone.utc).timestamp(), nullable=False)

