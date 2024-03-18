from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

POSTGRESS_DATABASE_URL = "postgresql://postgres:admin123@localhost:5000/postgres"
engine = create_engine(POSTGRESS_DATABASE_URL)  # Создаём движок

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)  # Создаём конструктор коннекшнов к базе

Base = declarative_base()  # Класс от которого будут наследовать Модели PSQL
