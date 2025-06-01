from crud_operations import UserCRUD, ScheduledMessageCRUD, CombinedOperations
from datetime import datetime, timedelta


def test_user_operations():
    """Тестирование операций с пользователями"""
    print("=== ТЕСТИРОВАНИЕ ПОЛЬЗОВАТЕЛЕЙ ===")

    # Создание пользователей
    print("1. Создание пользователей...")
    user1 = UserCRUD.create_user(
        username="testuser1",
        yandex_email="test1@yandex.ru",
        yandex_password="password123",
        yandex_calendar_link="http://calendar.yandex.ru/link1"
    )
    print(f"Создан пользователь: {user1}")

    user2 = UserCRUD.create_user(
        username="testuser2",
        yandex_email="test2@yandex.ru"
    )
    print(f"Создан пользователь: {user2}")

    # Получение пользователей
    print("\n2. Получение пользователей...")
    user_by_id = UserCRUD.get_user_by_id(user1.id)
    print(f"Пользователь по ID: {user_by_id}")

    user_by_username = UserCRUD.get_user_by_username("testuser1")
    print(f"Пользователь по username: {user_by_username}")

    user_by_email = UserCRUD.get_user_by_email("test2@yandex.ru")
    print(f"Пользователь по email: {user_by_email}")

    # Все пользователи
    all_users = UserCRUD.get_all_users()
    print(f"Всего пользователей: {len(all_users)}")

    # Поиск пользователей
    print("\n3. Поиск пользователей...")
    search_results = UserCRUD.search_users("test")
    print(f"Результаты поиска по 'test': {len(search_results)} пользователей")

    # Обновление пользователей
    print("\n4. Обновление пользователей...")
    updated_user = UserCRUD.update_user_by_id(
        user1.id,
        yandex_password="newpassword456"
    )
    print(f"Обновлен пользователь по ID: {updated_user}")

    updated_user2 = UserCRUD.update_user_by_username(
        "testuser2",
        yandex_calendar_link="http://calendar.yandex.ru/link2"
    )
    print(f"Обновлен пользователь по username: {updated_user2}")

    return user1.id, user2.id


def test_message_operations(user1_id, user2_id):
    """Тестирование операций с сообщениями"""
    print("\n=== ТЕСТИРОВАНИЕ СООБЩЕНИЙ ===")

    # Создание сообщений
    print("1. Создание сообщений...")
    future_time = datetime.now() + timedelta(hours=1)
    past_time = datetime.now() - timedelta(hours=1)

    message1 = ScheduledMessageCRUD.create_message(
        user_id=user1_id,
        title="Тестовое сообщение 1",
        content="Это первое тестовое сообщение",
        scheduled_time=future_time
    )
    print(f"Создано сообщение: {message1}")

    message2 = ScheduledMessageCRUD.create_message(
        user_id=user1_id,
        title="Прошедшее сообщение",
        content="Это сообщение должно быть готово к отправке",
        scheduled_time=past_time
    )
    print(f"Создано сообщение: {message2}")

    message3 = ScheduledMessageCRUD.create_message(
        user_id=user2_id,
        title="Сообщение пользователя 2",
        content="Сообщение от второго пользователя",
        scheduled_time=future_time
    )
    print(f"Создано сообщение: {message3}")

    # Получение сообщений
    print("\n2. Получение сообщений...")
    message_by_id = ScheduledMessageCRUD.get_message_by_id(message1.id)
    print(f"Сообщение по ID: {message_by_id}")

    user1_messages = ScheduledMessageCRUD.get_messages_by_user(user1_id)
    print(f"Сообщения пользователя 1: {len(user1_messages)}")

    all_messages = ScheduledMessageCRUD.get_all_messages()
    print(f"Всего сообщений: {len(all_messages)}")

    # Сообщения по времени
    print("\n3. Сообщения по времени...")
    pending_messages = ScheduledMessageCRUD.get_pending_messages()
    print(f"Готовые к отправке: {len(pending_messages)}")

    upcoming_messages = ScheduledMessageCRUD.get_upcoming_messages()
    print(f"Предстоящие сообщения: {len(upcoming_messages)}")

    upcoming_user1 = ScheduledMessageCRUD.get_upcoming_messages(user1_id)
    print(f"Предстоящие сообщения пользователя 1: {len(upcoming_user1)}")

    # Поиск сообщений
    print("\n4. Поиск сообщений...")
    search_results = ScheduledMessageCRUD.search_messages("тест")
    print(f"Результаты поиска по 'тест': {len(search_results)}")

    # Обновление сообщения
    print("\n5. Обновление сообщения...")
    updated_message = ScheduledMessageCRUD.update_message(
        message1.id,
        title="Обновленное сообщение",
        content="Обновленное содержимое"
    )
    print(f"Обновлено сообщение: {updated_message}")

    return message1.id, message2.id, message3.id


def test_combined_operations(user1_id, user2_id):
    """Тестирование комбинированных операций"""
    print("\n=== ТЕСТИРОВАНИЕ КОМБИНИРОВАННЫХ ОПЕРАЦИЙ ===")

    # Пользователь с сообщениями
    user_with_messages = CombinedOperations.get_user_with_messages(user1_id)
    print(f"Пользователь с сообщениями: {user_with_messages}")

    if user_with_messages:
        # Теперь сообщения будут загружены
        print(f"Количество сообщений у пользователя: {len(user_with_messages.scheduled_messages)}")

    # Подсчет сообщений
    messages_count = CombinedOperations.get_user_messages_count(user1_id)
    print(f"Количество сообщений пользователя 1: {messages_count}")


def test_delete_operations():
    """Тестирование операций удаления"""
    print("\n=== ТЕСТИРОВАНИЕ УДАЛЕНИЯ ===")

    # Создаем тестового пользователя для удаления
    test_user = UserCRUD.create_user(
        username="delete_test",
        yandex_email="delete@yandex.ru"
    )

    # Создаем сообщение для этого пользователя
    test_message = ScheduledMessageCRUD.create_message(
        user_id=test_user.id,
        title="Сообщение для удаления",
        content="Это сообщение будет удалено вместе с пользователем",
        scheduled_time=datetime.now() + timedelta(hours=1)
    )

    print(f"Создан тестовый пользователь для удаления: {test_user}")
    print(f"Создано тестовое сообщение: {test_message}")

    # Удаление сообщения
    message_deleted = ScheduledMessageCRUD.delete_message(test_message.id)
    print(f"Сообщение удалено: {message_deleted}")

    # Удаление пользователя по username
    user_deleted = UserCRUD.delete_user_by_username("delete_test")
    print(f"Пользователь удален по username: {user_deleted}")


def main():
    """Основная функция тестирования"""
    print("НАЧАЛО ТЕСТИРОВАНИЯ CRUD ОПЕРАЦИЙ")
    print("=" * 50)

    try:
        # Тестирование пользователей
        user1_id, user2_id = test_user_operations()

        # Тестирование сообщений
        message1_id, message2_id, message3_id = test_message_operations(user1_id, user2_id)

        # Тестирование комбинированных операций
        test_combined_operations(user1_id, user2_id)

        # Тестирование удаления
        test_delete_operations()

        print("\n" + "=" * 50)
        print("ВСЕ ТЕСТЫ ВЫПОЛНЕНЫ УСПЕШНО!")

        # Очистка тестовых данных
        print("\nОчистка тестовых данных...")
        UserCRUD.delete_user_by_id(user1_id)
        UserCRUD.delete_user_by_id(user2_id)
        print("Тестовые данные очищены")

    except Exception as e:
        print(f"ОШИБКА ПРИ ТЕСТИРОВАНИИ: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()