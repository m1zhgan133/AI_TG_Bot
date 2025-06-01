import sys
from mcp.server.fastmcp import FastMCP

from YandexCalendar.YC_get import *
from datetime import timezone


mcp = FastMCP("Server")



@mcp.tool(description="""
     give events from the Yandex calendar 
    
    Args:
    -----------
    caldav_calendar_url : str
        The full CalDAV URL for the calendar in format:
        'https://caldav.yandex.ru/calendars/user%40domain.com/events-12345/'
        Note: Email must be URL-encoded (%40 instead of @)
    
    username : str
        Full email address associated with the Yandex calendar account
        Example: 'user@custom-domain.com'
    
    password : str
        Password for the Yandex calendar account
    
    start_date : datetime | str | date | None, optional
        supported formats: 'YYYY-MM-DD', 'YYYY-MM-DD HH:MM'
        Start of date/time range for filtering events (inclusive).
        If None, no start filtering is applied.
    
    end_date : datetime | str | date | None, optional
        supported formats: 'YYYY-MM-DD', 'YYYY-MM-DD HH:MM'
        End of date/time range for filtering events (exclusive).
        If None, no end filtering is applied.
    
    Returns:
    --------
    list[dict]
        List of event dictionaries with the following structure:
        {
            "uid": str,                # Unique event ID
            "summary": str,            # Event title
            "description": str,        # Event description
            "dtstart": str,            # Formatted start time (YYYY-MM-DD HH:MM)
            "dtend": str,              # Formatted end time
            "location": str,           # Event location
            "timezone": str | None,    # Timezone ID (e.g., 'Europe/Moscow')
            "url": str                 # Original .ics URL for the event
        }
    
    Behavior Details:
    ----------------
    Error Handling:
       - Returns empty list for authentication errors
       - Logs but ignores individual event download errors
       - Raises exceptions only for fatal execution errors
       - Yandex may throttle requests if too many concurrent connections
    """)
async def get_calendar_event(
            caldav_calendar_url: str,
            username: str,
            password: str,
            start_date: datetime | str | date | None = None,
            end_date: datetime | str | date | None = None) -> list[dict]:
    events = await get_ycalendar_events(
        caldav_calendar_url,
        username,
        password,
        start_date,
        end_date)
    return events


# @mcp.tool(description="""
#     YOU DON'T KNOW TODAY'S DATE, ALWAYS USE THIS FUNCTION TO CHECK THE CURRENT DATE WHEN IT'S NECESSARY.
#     Returns current UTC date and time as formatted string.
#
#     Format: 'YYYY-MM-DD HH:MM:SS UTC'
#     Example: '2025-06-14 12:30:45 UTC'
#
#     Returns:
#         str: Current UTC timestamp in ISO-like format with timezone indicator
#     """)
# def get_utc_datetime() -> str:
#     return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")




@mcp.tool()
def Jonh(question: str):
    """Says his opition about event
    Args:
        question (str): question
    Returns:
        (str): His opinion
    """
    return "Я хочу в сушибар и не хочу баблти"

@mcp.tool()
def Misha(question: str):
    """Says his opition about event
    Args:
        question (str): question
    Returns:
        (str): His opinion
    """
    return "Я хочу в бар"

@mcp.tool()
def Gosha(question: str):
    """Says his opition about event
    Args:
        question (str): question
    Returns:
        (str): His opinion
    """
    return "Я хочу туда же куда и Михаил"

@mcp.tool()
def plus(number1: float, number2: float):
    """adds up 2 numbers
    Args:
        number1 (float): the first argument of addition
        number2 (float): the second argument of addition
    Returns:
        (float): result of addition
    """
    return number1 + number2




if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    mcp.run(transport=transport)
