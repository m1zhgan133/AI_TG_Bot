from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os
from dotenv import load_dotenv


# Настройка подключения к базе данных
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password123@localhost:5432/myapp_db")

engine = create_engine(DATABASE_URL, echo=False)  # echo=True для отладки SQL запросов
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)

    yandex_email = Column(String(100), unique=False, nullable=True)
    yandex_password = Column(String(100), unique=False, nullable=True)
    yandex_calendar_link = Column(String(200), unique=False, nullable=True)

    # Связь с запланированными сообщениями
    scheduled_messages = relationship("ScheduledMessage", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.yandex_email}')>"


class ScheduledMessage(Base):
    __tablename__ = "scheduled_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    is_sent = Column(Boolean, default=False)

    # Связь с пользователем
    user = relationship("User", back_populates="scheduled_messages")

    def __repr__(self):
        return f"<ScheduledMessage(id={self.id}, title='{self.title}', user_id={self.user_id})>"


# Функция для создания всех таблиц (если они не созданы через init.sql)
def create_tables():
    """Создание всех таблиц в базе данных"""
    Base.metadata.create_all(bind=engine)


# Функция для получения сессии базы данных
def get_db_session():
    """Получение новой сессии базы данных"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e


# Контекстный менеджер для работы с базой данных
class DatabaseSession:
    def __init__(self):
        self.db = None

    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db.rollback()
        self.db.close()


# Функция для проверки подключения к базе данных
def test_connection():
    """Тестирование подключения к базе данных"""
    try:
        with DatabaseSession() as db:
            db.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return False