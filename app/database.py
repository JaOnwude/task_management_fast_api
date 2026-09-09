import os
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session

# Render provides DATABASE_URL automatically when linking PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

# Render uses "postgres://" but SQLAlchemy requires "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session