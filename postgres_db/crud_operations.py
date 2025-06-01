from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_
# from models import User, ScheduledMessage, get_db_session
# используем следующую строку тк этот файл импортируется в бота и там какое то говно с путями
from postgres_db.models import User, ScheduledMessage, get_db_session
from datetime import datetime
from typing import List, Optional


class UserCRUD:
    """CRUD операции для пользователей"""

    @staticmethod
    def create_user(username: str, yandex_email: str = None,
                   yandex_password: str = None, yandex_calendar_link: str = None) -> User:
        """Создание нового пользователя"""
        db = get_db_session()
        try:
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
        finally:
            db.close()

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        db = get_db_session()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Получение пользователя по имени пользователя"""
        db = get_db_session()
        try:
            return db.query(User).filter(User.username == username).first()
        finally:
            db.close()

    @staticmethod
    def get_user_by_email(yandex_email: str) -> Optional[User]:
        """Получение пользователя по yandex_email"""
        db = get_db_session()
        try:
            return db.query(User).filter(User.yandex_email == yandex_email).first()
        finally:
            db.close()

    @staticmethod
    def get_all_users(skip: int = 0, limit: int = 100) -> List[User]:
        """Получение всех пользователей с пагинацией"""
        db = get_db_session()
        try:
            return db.query(User).offset(skip).limit(limit).all()
        finally:
            db.close()

    @staticmethod
    def update_user_by_id(user_id: int, **kwargs) -> Optional[User]:
        """Обновление данных пользователя по ID"""
        db = get_db_session()
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            if db_user:
                for key, value in kwargs.items():
                    if hasattr(db_user, key) and value is not None:
                        setattr(db_user, key, value)
                db.commit()
                db.refresh(db_user)
            return db_user
        finally:
            db.close()

    @staticmethod
    def update_user_by_username(username: str, **kwargs) -> Optional[User]:
        """Обновление данных пользователя по username"""
        db = get_db_session()
        try:
            db_user = db.query(User).filter(User.username == username).first()
            if db_user:
                for key, value in kwargs.items():
                    if hasattr(db_user, key) and value is not None:
                        setattr(db_user, key, value)
                db.commit()
                db.refresh(db_user)
            return db_user
        finally:
            db.close()

    @staticmethod
    def delete_user_by_id(user_id: int) -> bool:
        """Удаление пользователя по ID"""
        db = get_db_session()
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            if db_user:
                db.delete(db_user)
                db.commit()
                return True
            return False
        finally:
            db.close()

    @staticmethod
    def delete_user_by_username(username: str) -> bool:
        """Удаление пользователя по username"""
        db = get_db_session()
        try:
            db_user = db.query(User).filter(User.username == username).first()
            if db_user:
                db.delete(db_user)
                db.commit()
                return True
            return False
        finally:
            db.close()

    @staticmethod
    def search_users(search_term: str) -> List[User]:
        """Поиск пользователей по имени пользователя или yandex_email"""
        db = get_db_session()
        try:
            return db.query(User).filter(
                or_(
                    User.username.ilike(f"%{search_term}%"),
                    User.yandex_email.ilike(f"%{search_term}%")
                )
            ).all()
        finally:
            db.close()


class ScheduledMessageCRUD:
    """CRUD операции для запланированных сообщений"""

    @staticmethod
    def create_message(user_id: int, title: str, content: str, scheduled_time: datetime) -> ScheduledMessage:
        """Создание нового запланированного сообщения"""
        db = get_db_session()
        try:
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
        finally:
            db.close()

    @staticmethod
    def get_message_by_id(message_id: int) -> Optional[ScheduledMessage]:
        """Получение сообщения по ID"""
        db = get_db_session()
        try:
            return db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
        finally:
            db.close()

    @staticmethod
    def get_messages_by_user(user_id: int, skip: int = 0, limit: int = 100) -> List[ScheduledMessage]:
        """Получение всех сообщений пользователя"""
        db = get_db_session()
        try:
            return db.query(ScheduledMessage).filter(
                ScheduledMessage.user_id == user_id
            ).offset(skip).limit(limit).all()
        finally:
            db.close()

    @staticmethod
    def get_all_messages(skip: int = 0, limit: int = 100) -> List[ScheduledMessage]:
        """Получение всех запланированных сообщений"""
        db = get_db_session()
        try:
            return db.query(ScheduledMessage).offset(skip).limit(limit).all()
        finally:
            db.close()

    @staticmethod
    def get_pending_messages() -> List[ScheduledMessage]:
        """Получение всех сообщений готовых к отправке"""
        db = get_db_session()
        try:
            return db.query(ScheduledMessage).filter(
                ScheduledMessage.scheduled_time <= datetime.now()
            ).all()
        finally:
            db.close()

    @staticmethod
    def get_upcoming_messages(user_id: int = None) -> List[ScheduledMessage]:
        """Получение предстоящих сообщений"""
        db = get_db_session()
        try:
            query = db.query(ScheduledMessage).filter(
                ScheduledMessage.scheduled_time > datetime.now()
            )
            if user_id:
                query = query.filter(ScheduledMessage.user_id == user_id)
            return query.all()
        finally:
            db.close()

    @staticmethod
    def update_message(message_id: int, **kwargs) -> Optional[ScheduledMessage]:
        """Обновление запланированного сообщения"""
        db = get_db_session()
        try:
            db_message = db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
            if db_message:
                for key, value in kwargs.items():
                    if hasattr(db_message, key) and value is not None:
                        setattr(db_message, key, value)
                db.commit()
                db.refresh(db_message)
            return db_message
        finally:
            db.close()

    @staticmethod
    def delete_message(message_id: int) -> bool:
        """Удаление запланированного сообщения"""
        db = get_db_session()
        try:
            db_message = db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
            if db_message:
                db.delete(db_message)
                db.commit()
                return True
            return False
        finally:
            db.close()

    @staticmethod
    def search_messages(search_term: str, user_id: int = None) -> List[ScheduledMessage]:
        """Поиск сообщений по заголовку или содержимому"""
        db = get_db_session()
        try:
            query = db.query(ScheduledMessage).filter(
                or_(
                    ScheduledMessage.title.ilike(f"%{search_term}%"),
                    ScheduledMessage.content.ilike(f"%{search_term}%")
                )
            )
            if user_id:
                query = query.filter(ScheduledMessage.user_id == user_id)
            return query.all()
        finally:
            db.close()


# Дополнительные функции для работы с несколькими таблицами
class CombinedOperations:
    """Комбинированные операции для работы с обеими таблицами"""

    @staticmethod
    def get_user_with_messages(user_id: int) -> Optional[User]:
        """Получение пользователя со всеми его сообщениями"""
        db = get_db_session()
        try:
            # Явно загружаем сообщения вместе с пользователем
            user = db.query(User).options(
                selectinload(User.scheduled_messages)
            ).filter(User.id == user_id).first()
            return user
        finally:
            db.close()

    @staticmethod
    def get_user_messages_count(user_id: int) -> int:
        """Получение количества сообщений пользователя"""
        db = get_db_session()
        try:
            return db.query(ScheduledMessage).filter(ScheduledMessage.user_id == user_id).count()
        finally:
            db.close()

    @staticmethod
    def delete_user_with_messages_by_id(user_id: int) -> bool:
        """Удаление пользователя со всеми его сообщениями по ID"""
        return UserCRUD.delete_user_by_id(user_id)

    @staticmethod
    def delete_user_with_messages_by_username(username: str) -> bool:
        """Удаление пользователя со всеми его сообщениями по username"""
        return UserCRUD.delete_user_by_username(username)