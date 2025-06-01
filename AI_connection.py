from openai import AsyncClient
from os import getenv
from dotenv import load_dotenv


async def generate_response(promt):
    load_dotenv()
    client = AsyncClient(
        base_url="https://openrouter.ai/api/v1",
        api_key=getenv("MAI_DS_R1_TOKEN"),
    )

    completion = await client.chat.completions.create(
        extra_body={},
        model="microsoft/mai-ds-r1:free",
        messages=[
            {
                "role": "user",
                "content": promt
            }
        ]
    )
    return completion.choices[0].message.content