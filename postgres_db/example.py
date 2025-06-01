from models import DatabaseSession, test_connection
from crud_operations import UserCRUD, ScheduledMessageCRUD, CombinedOperations
from datetime import datetime, timedelta
import time


def demo_operations():
    """Демонстрация всех CRUD операций с новой структурой БД"""

    print("Проверка подключения к базе данных...")

    # Ожидание запуска базы данных
    max_attempts = 10
    for attempt in range(max_attempts):
        if test_connection():
            print("✓ Подключение к базе данных установлено")
            break
        else:
            print(f"⏳ Попытка подключения {attempt + 1}/{max_attempts}...")
            time.sleep(3)
    else:
        print("❌ Не удалось подключиться к базе данных")
        return

    # Использование контекстного менеджера для работы с БД
    try:
        with DatabaseSession() as db:
            print("\n=== ДЕМОНСТРАЦИЯ CRUD ОПЕРАЦИЙ ===\n")

            # 1. Создание пользователей
            print("1. Создание пользователей:")
            user1 = UserCRUD.create_user(
                db,
                username="john_doe",
                yandex_email="john@example.com",
                yandex_password="secret123",
                yandex_calendar_link="https://calendar.yandex.ru/john"
            )
            print(f"   ✓ Создан пользователь: {user1.username} (ID: {user1.id})")

            user2 = UserCRUD.create_user(
                db,
                username="jane_smith",
                yandex_email="jane@example.com"
            )
            print(f"   ✓ Создан пользователь: {user2.username} (ID: {user2.id})")

            # 2. Получение пользователей
            print("\n2. Получение пользователей:")
            retrieved_user = UserCRUD.get_user_by_id(db, user1.id)
            print(f"   → Пользователь по ID {user1.id}: {retrieved_user.username}")

            user_by_email = UserCRUD.get_user_by_email(db, "jane@example.com")
            print(f"   → Пользователь по email: {user_by_email.username}")

            all_users = UserCRUD.get_all_users(db)
            print(f"   → Всего пользователей: {len(all_users)}")

            # 3. Создание запланированных сообщений
            print("\n3. Создание запланированных сообщений:")
            message1 = ScheduledMessageCRUD.create_message(
                db,
                user_id=user1.id,
                title="Напоминание о встрече",
                content="Не забудь о встрече завтра в 10:00",
                scheduled_time=datetime.now() + timedelta(hours=1)
            )
            print(f"   ✓ Создано сообщение: {message1.title} (ID: {message1.id})")

            message2 = ScheduledMessageCRUD.create_message(
                db,
                user_id=user1.id,
                title="День рождения",
                content="Сегодня день рождения у мамы!",
                scheduled_time=datetime.now() + timedelta(days=1)
            )
            print(f"   ✓ Создано сообщение: {message2.title} (ID: {message2.id})")

            message3 = ScheduledMessageCRUD.create_message(
                db,
                user_id=user2.id,
                title="Оплата счетов",
                content="Не забыть оплатить коммунальные услуги",
                scheduled_time=datetime.now() + timedelta(days=5)
            )
            print(f"   ✓ Создано сообщение: {message3.title} (ID: {message3.id})")

            # 4. Получение сообщений
            print("\n4. Получение сообщений:")
            user1_messages = ScheduledMessageCRUD.get_messages_by_user(db, user1.id)
            print(f"   → Сообщений у {user1.username}: {len(user1_messages)}")
            for msg in user1_messages:
                print(f"     • {msg.title}")

            all_messages = ScheduledMessageCRUD.get_all_messages(db)
            print(f"   → Всего сообщений: {len(all_messages)}")

            upcoming_messages = ScheduledMessageCRUD.get_upcoming_messages(db)
            print(f"   → Предстоящих сообщений: {len(upcoming_messages)}")

            # 5. Обновление данных
            print("\n5. Обновление данных:")
            updated_user = UserCRUD.update_user(
                db,
                user1.id,
                yandex_calendar_link="https://new-calendar-link.ru"
            )
            print(f"   ✓ Обновлен календарь пользователя: {updated_user.yandex_calendar_link}")

            updated_message = ScheduledMessageCRUD.update_message(
                db,
                message1.id,
                title="ВАЖНО: Напоминание о встрече"
            )
            print(f"   ✓ Обновлен заголовок сообщения: {updated_message.title}")

            # 6. Поиск
            print("\n6. Поиск:")
            found_users = UserCRUD.search_users(db, "john")
            print(f"   → Найдено пользователей по запросу 'john': {len(found_users)}")

            found_messages = ScheduledMessageCRUD.search_messages(db, "встреча")
            print(f"   → Найдено сообщений по запросу 'встреча': {len(found_messages)}")

            # 7. Комбинированные операции
            print("\n7. Комбинированные операции:")
            user_with_messages = CombinedOperations.get_user_with_messages(db, user1.id)
            print(
                f"   → Пользователь {user_with_messages.username} имеет {len(user_with_messages.scheduled_messages)} сообщений")

            messages_count = CombinedOperations.get_user_messages_count(db, user2.id)
            print(f"   → У пользователя {user2.username} {messages_count} сообщений")

            # 8. Удаление
            print("\n8. Удаление:")
            deleted = ScheduledMessageCRUD.delete_message(db, message2.id)
            print(f"   ✓ Сообщение удалено: {deleted}")

            # Проверяем количество сообщений после удаления
            remaining_messages = ScheduledMessageCRUD.get_all_messages(db)
            print(f"   → Осталось сообщений: {len(remaining_messages)}")

            # 9. Удаление пользователя с сообщениями
            print("\n9. Удаление пользователя с сообщениями:")
            deleted_user = CombinedOperations.delete_user_with_messages(db, user2.id)
            print(f"   ✓ Пользователь удален: {deleted_user}")

            print("\n=== ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА ===")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_operations()