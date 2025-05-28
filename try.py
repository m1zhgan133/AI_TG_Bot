# Использование библиотеки caldav
import caldav

url = "https://caldav.yandex.ru"
username = "your_yandex_login"
password = "your_app_password"  # Специальный пароль для приложений

client = caldav.DAVClient(url, username=username, password=password)
principal = client.principal()
calendars = principal.calendars()

for calendar in calendars:
    events = calendar.events()
    for event in events:
        print(event.data)  # Вывод данных события в формате iCalendar