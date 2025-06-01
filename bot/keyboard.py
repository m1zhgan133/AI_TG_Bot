from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Этот объект будем использовать для скрытия клавиатуры
remove_keyboard = ReplyKeyboardRemove()

model_choice = ReplyKeyboardMarkup(resize_keyboard=True,
                                   input_field_placeholder='Выберете модель',
                                   keyboard=[
                                       # [KeyboardButton(text='MAI DeepSeak R1')] gpt-4o-mini
                                        [KeyboardButton(text='GPT-4o mini')]
                                   ])


guide_ycal = ReplyKeyboardMarkup(resize_keyboard=True,
                                   input_field_placeholder='Выберете вариант',
                                   keyboard=[
                                        [KeyboardButton(text='Гайд для телефона 📱'), KeyboardButton(text='Гайд для компьютера 💻')],
                                        [KeyboardButton(text='Добавить Яндекс календарь')]
                                   ])

