from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter, or_f
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

import keyboards.keybord_admin_main as kb
from config_data.config import Config, load_config
import database.requests as rq
from filter.admin_filter import check_super_admin, IsAdmin, IsSuperAdmin

import requests
import logging


router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()
user_dict = {}
user_dict_player = {}


class Admin(StatesGroup):
    get_name = State()


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    return response.json()


# запуск бота только администраторами /start
@router.message(CommandStart(), or_f(IsAdmin(), IsSuperAdmin()))
async def process_start_command(message: Message, state: FSMContext) -> None:
    """
    Запуск бота (нажата кнопка "Начать" или введена команда /start)
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_start_command: {message.chat.id}')
    await state.set_state(default_state)

    if not await check_super_admin(telegram_id=message.chat.id):
        await message.answer(text='Вы admin проекта',
                             reply_markup=kb.keyboards_admin_one())
        await message.answer(text='Отправьте мне ваше имя:')
        await state.set_state(Admin.get_name)
    else:
        data = {"token_auth": "SUPER_ADMIN",
                "telegram_id": message.chat.id,
                "username": f'super_admin_@{message.from_user.username}',
                "is_admin": rq.UserRole.admin}
        await rq.add_super_admin(data=data)
        await message.answer(text=f'Вы super_admin проекта',
                             reply_markup=kb.keyboards_superadmin_one())
        await message.answer(text='Отправьте мне ваше имя:')
        await state.set_state(Admin.get_name)


@router.message(F.text, IsAdmin(), StateFilter(Admin.get_name))
async def process_get_name_admin(message: Message, state: FSMContext) -> None:
    """
    Получаем имя администратора и обновляем его в БД
    :param message:
    :param state:
    :return:
    """
    await rq.set_username_admin(telegram_id=message.chat.id, username=message.text)
    await state.set_state(default_state)


@router.message(or_f(F.text == '>>>', F.text == '<<<'), IsAdmin())
async def process_change_keyboard(message: Message) -> None:
    """
    Пагинация по главному меню администратора и супер-администратора
    :param message:
    :return:
    """
    logging.info(f'process_change_keyboard: {message.chat.id}')
    if message.text == '>>>':
        if not await check_super_admin(telegram_id=message.chat.id):
            await message.answer(text='Вы admin проекта',
                                 reply_markup=kb.keyboards_admin_two())
        else:
            await message.answer(text='Вы super admin проекта',
                                 reply_markup=kb.keyboards_superadmin_two())
    if message.text == '<<<':
        if not await check_super_admin(telegram_id=message.chat.id):
            await message.answer(text='Вы admin проекта',
                                 reply_markup=kb.keyboards_admin_one())
        else:
            await message.answer(text='Вы super admin проекта',
                                 reply_markup=kb.keyboards_superadmin_one())
