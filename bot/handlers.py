from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import html, F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboard import *
from agent import *

router = Router()

class ActualModel(StatesGroup):
    MAI_DS_R1 = State()



@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!\nВыберите модель на которой будет работать ассистент",
                         reply_markup=model_choice)


@router.message(F.text == 'GPT-4o mini')
async def GPT_4o_mini_start(message: Message, state: FSMContext) -> None:
    await state.set_state(ActualModel.MAI_DS_R1)
    await message.answer(f'Вы начали чат с вашим ассистентом на основе GPT-4o mini.\nВы можете просить его:\n')


@router.message(ActualModel.MAI_DS_R1)
async def GPT_4o_mini_answer(message: Message) -> None:
    try:
        msg = await message.answer('Ответ генерируется...')
        response = await generate_response(message.text)
        await msg.delete()
        await message.reply(f'{response}')

    except TypeError:
        await message.answer("Неверный формат!")