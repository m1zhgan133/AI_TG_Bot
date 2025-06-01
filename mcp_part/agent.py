import asyncio
import os

from dotenv import find_dotenv, load_dotenv
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich import print as rprint

from langchain_openai import ChatOpenAI

from mcp_part.system_prompt import system_prompt


load_dotenv()
model = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                     model="gpt-4o-mini-2024-07-18",
                     temperature=0.0,
                     max_tokens=2000,
                     streaming=False)

def _log(ans):
    for message in ans['messages']:
        rprint(f"[{type(message).__name__}] {message.content} {getattr(message, 'tool_calls', '')}")


async def generate_response(prompt, user_data):
    server_params = StdioServerParameters(
        command="python",
        args=["..//mcp_part//server.py"],
    )


    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize() # Initialize the connection
            tools = await load_mcp_tools(session) # Get tools

            # Create and run the agent
            agent = create_react_agent(model, tools)

            agent_response = await agent.ainvoke({"messages": [
                {"role": "system", "content": system_prompt + '\n\nInformation about user:\n' + str(user_data)},
                {"role": "user", "content": prompt}]})
            _log(agent_response)

            # Извлекаем финальный ответ нейросети
            last_ai_message = next(
                 msg for msg in reversed(agent_response['messages'])
                 if f'{type(msg).__name__}' == 'AIMessage' # and not msg.tool_calls
                 )
            return last_ai_message.content

# print(asyncio.run(generate_response("Узнай у всех куда они хотят сходить и выбери одно место, а после сложи 15 и 7")))