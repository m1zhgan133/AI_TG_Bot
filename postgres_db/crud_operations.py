from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import User, ScheduledMessage
from datetime import datetime
from typing import List, Optional


class UserCRUD:
    """CRUD операции для пользователей"""

    @staticmethod
    def create_user(db: Session, username: str, yandex_email: str,
                   yandex_password: str = None, yandex_calendar_link: str = None) -> User:
        """Создание нового пользователя"""
        db_user = User(
            username=username,
            yandex_email=yandex_email,
            yandex_password=yandex_password,
            yandex_calendar_link=yandex_calendar_link
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Получение пользователя по имени пользователя"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, yandex_email: str) -> Optional[User]:
        """Получение пользователя по yandex_email"""
        return db.query(User).filter(User.yandex_email == yandex_email).first()

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение всех пользователей с пагинацией"""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
        """Обновление данных пользователя"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            for key, value in kwargs.items():
                if hasattr(db_user, key) and value is not None:
                    setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Удаление пользователя"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False

    @staticmethod
    def search_users(db: Session, search_term: str) -> List[User]:
        """Поиск пользователей по имени пользователя или yandex_email"""
        return db.query(User).filter(
            or_(
                User.username.ilike(f"%{search_term}%"),
                User.yandex_email.ilike(f"%{search_term}%")
            )
        ).all()


class ScheduledMessageCRUD:
    """CRUD операции для запланированных сообщений"""

    @staticmethod
    def create_message(db: Session, user_id: int, title: str, content: str,
                       scheduled_time: datetime) -> ScheduledMessage:
        """Создание нового запланированного сообщения"""
        db_message = ScheduledMessage(
            user_id=user_id,
            title=title,
            content=content,
            scheduled_time=scheduled_time
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    @staticmethod
    def get_message_by_id(db: Session, message_id: int) -> Optional[ScheduledMessage]:
        """Получение сообщения по ID"""
        return db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()

    @staticmethod
    def get_messages_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ScheduledMessage]:
        """Получение всех сообщений пользователя"""
        return db.query(ScheduledMessage).filter(
            ScheduledMessage.user_id == user_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_messages(db: Session, skip: int = 0, limit: int = 100) -> List[ScheduledMessage]:
        """Получение всех запланированных сообщений"""
        return db.query(ScheduledMessage).offset(skip).limit(limit).all()

    @staticmethod
    def get_pending_messages(db: Session) -> List[ScheduledMessage]:
        """Получение всех сообщений готовых к отправке"""
        return db.query(ScheduledMessage).filter(
            ScheduledMessage.scheduled_time <= datetime.now()
        ).all()

    @staticmethod
    def get_upcoming_messages(db: Session, user_id: int = None) -> List[ScheduledMessage]:
        """Получение предстоящих сообщений"""
        query = db.query(ScheduledMessage).filter(
            ScheduledMessage.scheduled_time > datetime.now()
        )
        if user_id:
            query = query.filter(ScheduledMessage.user_id == user_id)
        return query.all()

    @staticmethod
    def update_message(db: Session, message_id: int, **kwargs) -> Optional[ScheduledMessage]:
        """Обновление запланированного сообщения"""
        db_message = db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
        if db_message:
            for key, value in kwargs.items():
                if hasattr(db_message, key) and value is not None:
                    setattr(db_message, key, value)
            db.commit()
            db.refresh(db_message)
        return db_message

    @staticmethod
    def delete_message(db: Session, message_id: int) -> bool:
        """Удаление запланированного сообщения"""
        db_message = db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
        if db_message:
            db.delete(db_message)
            db.commit()
            return True
        return False

    @staticmethod
    def search_messages(db: Session, search_term: str, user_id: int = None) -> List[ScheduledMessage]:
        """Поиск сообщений по заголовку или содержимому"""
        query = db.query(ScheduledMessage).filter(
            or_(
                ScheduledMessage.title.ilike(f"%{search_term}%"),
                ScheduledMessage.content.ilike(f"%{search_term}%")
            )
        )
        if user_id:
            query = query.filter(ScheduledMessage.user_id == user_id)
        return query.all()


# Дополнительные функции для работы с несколькими таблицами
class CombinedOperations:
    """Комбинированные операции для работы с обеими таблицами"""

    @staticmethod
    def get_user_with_messages(db: Session, user_id: int) -> Optional[User]:
        """Получение пользователя со всеми его сообщениями"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_messages_count(db: Session, user_id: int) -> int:
        """Получение количества сообщений пользователя"""
        return db.query(ScheduledMessage).filter(ScheduledMessage.user_id == user_id).count()

    @staticmethod
    def delete_user_with_messages(db: Session, user_id: int) -> bool:
        """Удаление пользователя со всеми его сообщениями"""
        # Благодаря cascade="all, delete-orphan" в модели,
        # сообщения удалятся автоматически
        return UserCRUD.delete_user(db, user_id)