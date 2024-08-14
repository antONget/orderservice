from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter

from filter.admin_filter import IsAdmin
import keyboards.keyboard_attach_resource as kb
import database.requests as rq
from config_data.config import Config, load_config

import logging
import requests

router = Router()
config: Config = load_config()


class Channel(StatesGroup):
    id_channel = State()
    id_group = State()


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    return response.json()


# Прикрепить - [Канал][Беседа]
@router.message(F.text == 'Прикрепить', IsAdmin())
async def process_change_channel(message: Message) -> None:
    """
    Функция получает id канала или чата для отправки отчета
    :param message:
    :return:
    """
    logging.info(f'process_change_channel: {message.chat.id}')
    await message.answer(text='Добавьте/замените канал или беседу',
                         reply_markup=kb.keyboard_append_channel_and_group())


# Прикрепить - Канал
@router.callback_query(F.data == 'add_channel')
async def process_add_channel(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_add_channel: {callback.message.chat.id}')
    await callback.message.edit_text(text='Пришлите id канал!',
                                     reply_markup=None)
    await state.set_state(Channel.id_channel)
    await callback.answer()


# Прикрепить - Канал - добавление/замена канала в базе
@router.message(StateFilter(Channel.id_channel), IsAdmin())
async def process_change_list_users(message: Message, state: FSMContext) -> None:
    logging.info(f'process_change_list_users: {message.chat.id}')
    try:
        channel_id = int(message.text)
    except:
        await message.answer(text='Пришлите id канала. ID должно быть целым числом')
        return
    channel = get_telegram_user(channel_id, config.tg_bot.token)
    if 'result' in channel:
        data = {"channel_id": channel_id, "type": 'channel'}
        await rq.add_resource(data=data)
        await message.answer(text=f'Вы установили канал\n @{channel["result"]["title"]}\n id={message.text}'
                                  f' для получения отчетов!')
    else:
        await message.answer(text=f'Канал id={message.text} не корректен, или бот не является администратором!')
    await state.set_state(default_state)


# Прикрепить - Беседа
@router.callback_query(F.data == 'add_group')
async def process_add_group(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'add_group: {callback.message.chat.id}')
    await callback.message.edit_text(text='Пришлите id беседы!',
                                     reply_markup=None)
    await state.set_state(Channel.id_group)
    await callback.answer()


# Прикрепить - Канал - добавление/замена канала в базе
@router.message(StateFilter(Channel.id_group), IsAdmin())
async def process_change_list_group(message: Message, state: FSMContext) -> None:
    logging.info(f'process_change_list_group: {message.chat.id}')
    try:
        channel_id = int(message.text)
    except:
        await message.answer(text='Пришлите id канала.  ID должно быть целым числом')
        return
    channel = get_telegram_user(channel_id, config.tg_bot.token)
    if 'result' in channel:
        data = {"channel_id": int(message.text), "type": 'group'}
        await rq.add_resource(data=data)
        await message.answer(text=f'Вы установили беседу\n @{channel["result"]["title"]}\n id={message.text}'
                                  f' для получения отчетов!')
    else:
        await message.answer(text=f'Канал/чат id={message.text} не корректен, или бот не является администратором!')
    await state.set_state(default_state)
