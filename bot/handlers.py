from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, InputMediaPhoto
from aiogram import html, F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.utils.chat_member import USERS
from aiogram.utils.media_group import MediaGroupBuilder
import psycopg2

from keyboard import *
from mcp_part.agent import *
from postgres_db.crud_operations import *

router = Router()

class ActualState(StatesGroup):
    GPT_4o_mini = State()

    reg_ycal_start = State()
    reg_ycal_email = State()
    reg_ycal_caldav = State()
    reg_ycal_key = State()


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        UserCRUD.create_user(username=message.from_user.username)
        print(f'-------------- пользователь с ником {message.from_user.username} успешно зарегистрировался --------------')
    except Exception as e:
        pass

    start_text = (
        f"Привет, {html.bold(message.from_user.full_name)}!\n"
        f'Я ваш {html.bold('ИИ ассистент.')}\n\n'
        f'{html.bold('Вот что я могу:')}\n'
        f'{html.bold('1)')} Общаться с вами и отвечать на любые вопросы\n'
        f'{html.bold('2)')} Взаимодействовать с вашим календарем\n'
        f'для этого нужно подключить его /registrate_Ycal\n'
        f'{html.bold('3)')} Отправлять вам отложенные сообщения\n'
        f'{html.bold('4)')} Вы можете использовать голосовые сообщения для общения со мной\n\n'
        f'Теперь выберите модель на которой будет работать ассистент или добавьте свой календарь.'
    )
    await message.answer(start_text,
                         reply_markup=model_choice)


@router.message(F.text == 'GPT-4o mini')
async def GPT_4o_mini_start(message: Message, state: FSMContext) -> None:
    await state.set_state(ActualState.GPT_4o_mini)
    start_text = (
        'Вы начали чат с вашим ассистентом на основе GPT-4o mini. ✅\n'
        'Чтобы закончить чат введите /start'
    )
    await message.answer(start_text,
        reply_markup=remove_keyboard  # Вот эта строка скроет клавиатуру
    )


@router.message(ActualState.GPT_4o_mini)
async def GPT_4o_mini_answer(message: Message) -> None:
    try:
        msg = await message.answer('Ответ генерируется...')

        user = UserCRUD.get_user_by_username(username=message.from_user.username)
        user_data = {
            'username': user.username,
            'yandex_email': user.yandex_email,
            'yandex_password': user.yandex_password,
            'yandex_calendar_link': user.yandex_calendar_link
        }
        response = await generate_response(message.text, user_data=user_data)
        await msg.delete()
        await message.reply(f'{response}')

    except TypeError:
        await message.answer("Неверный формат!")


# --------------------------------------------- регистрация яндекс почты ---------------------------------------------

@router.message(Command('registrate_Ycal'))
async def command_reg_ycal_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(ActualState.reg_ycal_start)
    await message.answer("""Это регистрация яндекс календаря, позволит ассистенту просматривать и добавлять записи в календарь по вашим запросам. Это может быть очень удобно и может помочь в вашей жизни и работе.
Если не хотите продолжать введите /start
 
Что бы привязать календарь вам необходимо предоставить нам: 
1) вашу почту ✉️
2) CalDAV ссылку на ваш календарь 📅
3) сгенерировать ключ, чтобы бот получил доступ к вашим событиям 🔑

Если вы не знаете где взять ключ и CalDAV ссылку на ваш календарь можете посмотреть гайд.
                         """,
                         reply_markup=guide_ycal)


# Хендлеры для гайдов
@router.message(StateFilter(ActualState.reg_ycal_start), F.text == 'Гайд для телефона 📱')
async def phone_guide_handler(message: Message, state: FSMContext) -> None:
    guide_text_1 = (
        '📱 <b>Гайд для телефона:</b>\n\n'
        'Чтобы получить CalDAV ссылку на ваш календарь:\n'
        '1) Зайдите в ваш календарь в браузере 📅\n'
        'https://calendar.yandex.ru/week\n'
        '2) Перейдите в версию для компьютера\n'
        '3) Нажмите на иконку настроек рядом с интересующем календарем ⚙️\n'
        '4) Нажмите на "Экспорт" и скопируйте CalDAV ссылку'
    )
    # Создаем альбом из картинок
    album_builder = MediaGroupBuilder()

    # Добавляем картинки
    album_builder.add_photo(
        media=FSInputFile("pictures/ycal_phone_guide_1.jpg")
    )
    album_builder.add_photo(
        media=FSInputFile("pictures/ycal_PC_guide_1.png")
    )
    album_builder.add_photo(
        media=FSInputFile("pictures/ycal_PC_guide_2.png"),
        caption=guide_text_1  # Ограничение 1024 символа для подписи
    )
    # Отправляем альбом
    await message.answer_media_group(media=album_builder.build())


    guide_text_2 = (
        'Чтобы получить ключ который даст ассистенту доступ к вашему календарю:\n'
        '1) Перейдите по ссылке в <a href="https://id.yandex.ru/security/app-passwords">настройки паролей приложений</a>\n'
        '2) Создайте пароль приложения для календаря'
    )
    # Создаем альбом из картинок
    album_builder = MediaGroupBuilder()

    album_builder.add_photo(
        media=FSInputFile("pictures/ycal_PC_guide_3.png"),
        caption=guide_text_2  # Ограничение 1024 символа для подписи
    )
    # Отправляем альбом
    await message.answer_media_group(media=album_builder.build())


@router.message(StateFilter(ActualState.reg_ycal_start), F.text == 'Гайд для компьютера 💻')
async def pc_guide_handler(message: Message, state: FSMContext) -> None:
    guide_text_1 = (
        '💻 <b>Гайд для компьютера</b>\n\n'
        'Чтобы получить CalDAV ссылку на ваш календарь:\n'
        '1) Зайдите в ваш <a href="https://calendar.yandex.ru/week">календарь</a> 📅\n'
        '2) Нажмите на иконку настроек рядом с интересующем календарем ⚙️\n'
        '3) Нажмите на "Экспорт" и скопируйте CalDAV ссылку'
    )
    # Создаем альбом из картинок
    album_builder = MediaGroupBuilder()

    # Добавляем картинки
    album_builder.add_photo(
        media=FSInputFile("pictures/ycal_PC_guide_1.png")
    )
    album_builder.add_photo(
        media=FSInputFile("pictures/ycal_PC_guide_2.png"),
        caption=guide_text_1  # Ограничение 1024 символа для подписи
    )
    # Отправляем альбом
    await message.answer_media_group(media=album_builder.build())


    guide_text_2 = (
        'Чтобы получить ключ который даст ассистенту доступ к вашему календарю:\n'
        '1) Перейдите по ссылке в <a href="https://id.yandex.ru/security/app-passwords">настройки паролей приложений</a>\n'
        '2) Создайте пароль приложения для календаря'
    )
    # Создаем альбом из картинок
    album_builder = MediaGroupBuilder()

    album_builder.add_photo(
        media=FSInputFile("pictures/ycal_PC_guide_3.png"),
        caption=guide_text_2  # Ограничение 1024 символа для подписи
    )
    # Отправляем альбом
    await message.answer_media_group(media=album_builder.build())



# Хендлеры для ввода данных
@router.message(StateFilter(ActualState.reg_ycal_start), F.text == 'Добавить Яндекс календарь')
async def start_email_input(message: Message, state: FSMContext) -> None:
    await state.set_state(ActualState.reg_ycal_email)
    await message.answer(
        "Введите вашу почту, привязанную к Яндекс.Календарю:",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(StateFilter(ActualState.reg_ycal_email))
async def process_email(message: Message, state: FSMContext) -> None:
    # Здесь должна быть валидация почты (пропущена по условию)
    await state.set_state(ActualState.reg_ycal_caldav)
    await state.update_data(email=message.text)
    await message.answer("Теперь введите CalDAV ссылку на календарь:")

@router.message(StateFilter(ActualState.reg_ycal_caldav))
async def process_caldav(message: Message, state: FSMContext) -> None:
    await state.set_state(ActualState.reg_ycal_key)
    await state.update_data(caldav_url=message.text)
    await message.answer("Введите пароль приложения(календаря):")

@router.message(StateFilter(ActualState.reg_ycal_key))
async def process_key(message: Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    email = user_data.get("email")
    caldav_url = user_data.get("caldav_url")
    key = message.text

    try:
        UserCRUD.update_user_by_username(username=message.from_user.username, yandex_email=email ,yandex_password=key ,yandex_calendar_link=caldav_url )
        answer_text = (
            "Регистрация календаря завершена! Данные сохранены.\n"
            "Внимание!! Если вы ввели некорректные данные ассистент не сможет получить доступ к вашему календарю.\n\n"
            "Введите /start чтобы вернуться в главное меню."
        )
        await message.answer(answer_text)
    except Exception as e:
        await message.answer('Произошла ошибка')
        print('Ошибка при обновлении данных календаря', e, sep='\n')


    # Здесь будет ваша логика обработки данных
    await state.clear()  # Очищаем состояние


# --------------------------------------------- админские команды ---------------------------------------------
@router.message(Command('admin_get_all_users'))
async def admin_get_all_users(message: Message, state: FSMContext) -> None:
    if os.getenv('admin_username') == message.from_user.username:
        await message.answer(str(UserCRUD.get_all_users()), parse_mode=None)