from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message
from lexicon.lexicon_ru import MESSAGE_TEXT
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from keyboards.keyboards import *
from aiogram.types import CallbackQuery
from secrets import token_urlsafe
import asyncio
from module.data_base import check_command_for_admins, table_users, check_command_for_user
import logging
from config_data.config import Config, load_config
from module.data_base import check_token

router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class User(StatesGroup):
    get_token = State()
    auth_token = State()


# запуск бота пользователем /start
@router.message(CommandStart())
async def process_start_command_user(message: Message, state: FSMContext) -> None:
    table_users()
    logging.info(f'process_start_command_user: {message.chat.id}')
    if not check_command_for_user:
        await message.answer(text='Для авторизации в боте пришлите токен который вам отправил администратор')
        await state.set_state(User.get_token)
    else:
        await message.answer(text='Вы авторизованы в боте, и можете получать заказы на услуги')


# проверяем TOKEN
@router.message(F.text, StateFilter(User.get_token))
async def get_token_user(message: Message, state: FSMContext) -> None:
    logging.info(f'get_token_user: {message.chat.id}')
    if check_token(message):
        await message.answer(text='Вы добавлены')
        await state.set_state(User.auth_token)
    else:
        await message.answer(text='TOKEN не прошел верификацию. Попробуйте с другим токеном')


# рекция пользователя на заказ
@router.callback_query(F.data.startswith('ready'))
async def process_pass_edit_service(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_pass_edit_service: {callback.message.chat.id}')
    ready = callback.data.split('_')[1]
    if ready == 'yes':
        await callback.message.answer(text=f'Отлично вы в команде!')
    else:
        await callback.message.answer(text=f'Жаль, выполнит заказ другой')
