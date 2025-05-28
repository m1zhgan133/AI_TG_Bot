from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


model_choice = ReplyKeyboardMarkup(resize_keyboard=True,
                                   input_field_placeholder='Выберете модель',
                                   keyboard=[
                                       # [KeyboardButton(text='MAI DeepSeak R1')] gpt-4o-mini
                                        [KeyboardButton(text='GPT-4o mini')]
                                   ])

