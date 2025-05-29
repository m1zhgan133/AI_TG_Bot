import asyncio
import aiohttp

from icalendar import Calendar
from datetime import datetime



async def change_yandex_calendar(caldav_calendar_url: str, username: str, password: str, new_events='') -> None:
    """Function for deleting events and creating new ones"""
    host = "https://caldav.yandex.ru"
    auth = aiohttp.BasicAuth(login=username, password=password)
    async with aiohttp.ClientSession() as session:
        async with session.request(method="GET", url=caldav_calendar_url, auth=auth) as resp:
            # Получаем все события в формате:
            # /calendars/<username>%40yandex.ru/events-33720679/211ymv64gd3osmgaf1ic9yandex.ru.ics
            ics_urls = await resp.text()

            # Обрабатываем список URL
            event_urls = [url.strip() for url in ics_urls.split('\n') if url.strip()]

            # Создаем задачи для асинхронной обработки
            tasks = []
            for rel_url in event_urls:
                full_url = f"{host}{rel_url}"
                tasks.append(fetch_and_parse_event(session, full_url, auth))

            # Выполняем все задачи параллельно
            all_events = await asyncio.gather(*tasks)

        # Фильтруем None (ошибки) и выводим результат
        parsed_events = [event for event in all_events if event is not None]
        print(f"\nSuccessfully parsed {len(parsed_events)} events:")
        for event in parsed_events:
            print(f"- {event['summary']} ({event['dtstart']} to {event['dtend']})")

        return parsed_events

async def fetch_and_parse_event(session: aiohttp.ClientSession, url: str, auth: aiohttp.BasicAuth) -> dict:
    """Загружает и парсит отдельное событие"""
    try:
        async with session.get(url, auth=auth) as response:
            ics_data = await response.text()

            # Парсинг .ics файла
            cal = Calendar.from_ical(ics_data)
            for component in cal.walk():
                if component.name == "VEVENT":
                    return {
                        "uid": str(component.get("uid")),
                        "summary": str(component.get("summary", "No title")),
                        "description": str(component.get("description", "")),
                        "dtstart": format_datetime(component.get("dtstart")),
                        "dtend": format_datetime(component.get("dtend")),
                        "location": str(component.get("location", "")),
                        "url": url
                    }
        return None
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return None

def format_datetime(dt) -> str:
    """Конвертирует datetime в читаемый формат"""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M")
    return str(dt.dt) if hasattr(dt, 'dt') else "Unknown"


        # for ics_uid in ics_urls.splitlines():
        #     if ics_uid != "$":
        #         async with session.request(method="DELETE", url=host + ics_uid, auth=auth):
        #             pass
        # async with session.request(method="PUT", url=caldav_calendar_url + ' ', auth=auth, data=new_events):
        #     pass


if __name__ == '__main__':
    # asyncio.run(change_yandex_calendar(
    #     caldav_calendar_url="https://caldav.yandex.ru/calendars/MikhailYashenkov%40yandex.ru/events-33720679/",
    #     # new_events=""".ics text""",
    #     username='MikhailYashenkov',
    #     password='bbutejkbcdwsadpb'))

    asyncio.run(change_yandex_calendar(
        caldav_calendar_url="https://caldav.yandex.ru/calendars/m.yashenkov%40edu.centraluniversity.ru/events-30752253/",
        # new_events=""".ics text""",
        username='m.yashenkov',
        password='bgqjcwplypmxxjoz'))