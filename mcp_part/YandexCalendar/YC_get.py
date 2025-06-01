import asyncio
import aiohttp
from icalendar import Calendar, vDDDTypes
from datetime import datetime, date, timedelta, timezone
import re

# Ограничение на параллельные запросы
MAX_CONCURRENT_REQUESTS = 20


async def get_ycalendar_events(
        caldav_calendar_url: str,
        username: str,
        password: str,
        start_date: datetime | str | date | None = None,
        end_date: datetime | str | date | None = None
) -> list:
    """Function for working with Yandex Calendar with time filtering"""
    # if str, превращаем из строки в datetime
    if isinstance(start_date, str):
        try:
            # Try without seconds
            start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        except ValueError:
            try:
                # Try date only
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                print(f"Warning: Invalid start_date format '{start_date}'. Using None.")
                start_date = None

    if isinstance(end_date, str):
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        except ValueError:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                print(f"Warning: Invalid end_date format '{end_date}'. Using None.")
                end_date = None

    # Функция для нормализации часовых поясов
    def normalize_datetime(dt):
        """Convert to UTC timezone-aware datetime"""
        if isinstance(dt, datetime):
            if dt.tzinfo is None:
                # Считаем наивные datetime UTC
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        return dt

    # Нормализуем входные даты
    start_date = normalize_datetime(start_date) if start_date else None
    end_date = normalize_datetime(end_date) if end_date else None

    host = "https://caldav.yandex.ru"
    auth = aiohttp.BasicAuth(login=username, password=password)
    all_events = []

    # Создаем семафор для ограничения одновременных запросов
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit_per_host=50),
            timeout=aiohttp.ClientTimeout(total=60, connect=30, sock_read=30)
    ) as session:
        # 1. Проверяем доступность календаря и получаем корректные ссылки
        async with session.request(method="GET", url=caldav_calendar_url, auth=auth) as resp:
            if resp.status != 200:
                error_content = await resp.text()
                print(f"Calendar access error [{resp.status}]: {error_content[:200]}")
                return []

            content_type = resp.headers.get('Content-Type', '')
            if 'text/html' in content_type:
                print("Received HTML instead of calendar data. Possible authentication issue.")
                return []

            ics_urls = await resp.text()
            print(f"Received calendar data with {len(ics_urls.splitlines())} lines")

        # 2. Фильтрация и нормализация URL
        event_urls = []
        for line in ics_urls.split('\n'):
            url = line.strip()
            if url and url.endswith('.ics'):
                clean_url = re.sub(r'<[^>]+>', '', url)
                clean_url = clean_url.replace('@', '%40')
                event_urls.append(clean_url)

        print(f"Found {len(event_urls)} valid .ics URLs")

        # 3. Создаем задачи с ограничением параллелизма
        tasks = []
        for url in event_urls:
            full_url = f"{host}{url}"
            task = asyncio.create_task(
                fetch_and_parse_event_with_semaphore(
                    session, full_url, auth, semaphore
                )
            )
            tasks.append(task)

        # 4. Обрабатываем результаты
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 5. Фильтруем события по времени и ошибкам
        for result in results:
            if isinstance(result, Exception):
                print(f"Event processing error: {str(result)}")
            elif result:
                event_start = result.get("dtstart_obj")
                if not event_start:
                    all_events.append(result)
                    continue

                # Нормализуем время события
                if isinstance(event_start, datetime):
                    if event_start.tzinfo is None:
                        # Считаем наивные datetime UTC
                        event_start = event_start.replace(tzinfo=timezone.utc)
                    else:
                        event_start = event_start.astimezone(timezone.utc)

                # Для событий целого дня
                elif isinstance(event_start, date):
                    event_start = datetime(
                        event_start.year,
                        event_start.month,
                        event_start.day,
                        tzinfo=timezone.utc
                    )

                # Проверяем начало события
                in_range = True
                if start_date:
                    if isinstance(start_date, date) and not isinstance(start_date, datetime):
                        start_comp = datetime(
                            start_date.year,
                            start_date.month,
                            start_date.day,
                            tzinfo=timezone.utc
                        )
                    else:
                        start_comp = start_date

                    in_range = in_range and (event_start >= start_comp)

                if end_date:
                    if isinstance(end_date, date) and not isinstance(end_date, datetime):
                        end_comp = datetime(
                            end_date.year,
                            end_date.month,
                            end_date.day,
                            tzinfo=timezone.utc
                        ) + timedelta(days=1)
                    else:
                        end_comp = end_date

                    in_range = in_range and (event_start < end_comp)

                if in_range:
                    result.pop("dtstart_obj", None)
                    result.pop("dtend_obj", None)
                    all_events.append(result)

        print(f"Found {len(all_events)} events matching time criteria")
        return all_events


async def fetch_and_parse_event_with_semaphore(
        session: aiohttp.ClientSession,
        url: str,
        auth: aiohttp.BasicAuth,
        semaphore: asyncio.Semaphore,
        max_retries: int = 3
) -> dict:
    """Fetch event with semaphore control and retries"""
    async with semaphore:
        for attempt in range(max_retries):
            try:
                return await fetch_and_parse_event(session, url, auth)
            except (aiohttp.ClientConnectorError,
                    aiohttp.ServerDisconnectedError,
                    asyncio.TimeoutError,
                    aiohttp.ClientOSError) as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Экспоненциальная задержка
                    print(f"Retrying {url} in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    raise e


async def fetch_and_parse_event(session: aiohttp.ClientSession, url: str, auth: aiohttp.BasicAuth) -> dict:
    """Load and parse single event"""
    try:
        # Проверка URL
        if '<' in url or '>' in url:
            raise ValueError(f"Invalid URL format: {url}")

        async with session.get(url, auth=auth) as response:
            if response.status != 200:
                error_content = await response.text()
                print(f"Error fetching {url}: {response.status} - {error_content[:100]}")
                return None

            ics_data = await response.text()
            cal = Calendar.from_ical(ics_data)

            for component in cal.walk():
                if component.name == "VEVENT":
                    return parse_event_component(component, url)

        return None
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        raise


def parse_event_component(component, url: str) -> dict:
    """Parse VEVENT component with original time objects"""
    dtstart = component.get("dtstart")
    dtend = component.get("dtend")

    # Сохраняем оригинальные объекты времени
    dtstart_obj = dtstart.dt if dtstart else None
    dtend_obj = dtend.dt if dtend else None

    # Извлекаем информацию о часовом поясе
    tzid = None
    if dtstart and hasattr(dtstart, 'params') and "TZID" in dtstart.params:
        tzid = dtstart.params["TZID"]

    return {
        "uid": safe_get(component, "uid"),
        "summary": safe_get(component, "summary", "No title"),
        "description": safe_get(component, "description"),
        "dtstart": format_datetime(dtstart_obj),
        "dtend": format_datetime(dtend_obj),
        "location": safe_get(component, "location"),
        "timezone": tzid,
        "url": url,
        # Сохраняем оригинальные объекты для фильтрации
        "dtstart_obj": dtstart_obj,
        "dtend_obj": dtend_obj
    }


def safe_get(component, prop_name, default=""):
    """Safely get property from iCalendar component"""
    value = component.get(prop_name)
    if value is None:
        return default
    return str(value)


def format_datetime(dt) -> str:
    """Convert datetime/date to readable format"""
    if not dt:
        return "Unknown"

    if isinstance(dt, datetime):
        if dt.tzinfo:
            return dt.strftime("%Y-%m-%d %H:%M %Z")
        return dt.strftime("%Y-%m-%d %H:%M")

    if isinstance(dt, date):
        return dt.strftime("%Y-%m-%d")

    return str(dt)

    # for ics_uid in ics_urls.splitlines():
    #     if ics_uid != "$":
    #         async with session.request(method="DELETE", url=host + ics_uid, auth=auth):
    #             pass
    # async with session.request(method="PUT", url=caldav_calendar_url + ' ', auth=auth, data=new_events):
    #     pass


if __name__ == '__main__':
    # print(asyncio.run(get_ycalendar_events(
    #         caldav_calendar_url="https://caldav.yandex.ru/calendars/MikhailYashenkov%40yandex.ru/events-33720679/",
    #         # new_events=""".ics text""",
    #         username='MikhailYashenkov',
    #         password='bbutejkbcdwsadpb',
    #         start_date='2025-05-26',
    #         end_date='2025-06-01'
    #     )))


    for x in asyncio.run(get_ycalendar_events(
            caldav_calendar_url="https://caldav.yandex.ru/calendars/m.yashenkov%40edu.centraluniversity.ru/events-30752253/",
            # new_events=""".ics text""",
            username='m.yashenkov@edu.centraluniversity.ru',
            password='bgqjcwplypmxxjoz',
            start_date='2025-05-26',
            end_date='2025-06-01'
        )):
        print(x)
