'''
Contains the function to create both the database
and get a connection to the database.
'''

import os

from collections.abc import Generator
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql import text


DATABASE_NAME = os.environ.get('ACCOUNT_DB_NAME')

DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')

DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_PORT = os.environ.get('DATABASE_PORT')

GENERAL_DATABASE_URL = f'postgresql+psycopg2://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}'

DATABASE_URL = GENERAL_DATABASE_URL + f'/{DATABASE_NAME}'
POSTGRES_DATABASE_URL = GENERAL_DATABASE_URL + '/postgres'

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Dependency to get DB session
@contextmanager
def get_db_conn() -> Generator[Session, None, None]:
    '''
    This file gives out the object connection to the specified database
    
    yeild (Session, None, None): only yeilds the database connection
    '''

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def database_initialization(database_name: str=DATABASE_NAME) -> None:
    '''
    This function checks whether the database has been created.
    If not the database is created on server startup.

    database_name (str): url route to the desired database

    return (None):
    '''

    print('Initializing Database And Connection')

    checking_engine = create_engine(POSTGRES_DATABASE_URL, isolation_level="AUTOCOMMIT")

    with checking_engine.connect() as conn:
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{database_name}'"))
        exists = result.scalar() is not None

        if not exists:
            conn.execute(text(f"CREATE DATABASE {database_name}"))
            print(f'- Database ({database_name}) Previously Not Existing Now Created')
