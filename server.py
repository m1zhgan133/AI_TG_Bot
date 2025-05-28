import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Server")

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
