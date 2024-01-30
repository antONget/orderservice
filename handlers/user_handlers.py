import random

from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from keyboards.keyboards import *
from aiogram.types import CallbackQuery
import json
import asyncio
from module.data_base import check_command_for_admins, table_users, check_command_for_user, get_row_orders_id, \
    update_list_players, get_channel
import logging
from config_data.config import Config, load_config
from module.data_base import check_token

router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class User(StatesGroup):
    get_token = State()
    auth_token = State()
    report = State()


# запуск бота пользователем /start
@router.message(CommandStart())
async def process_start_command_user(message: Message, state: FSMContext) -> None:
    table_users()
    logging.info(f'process_start_command_user: {message.chat.id}')
    if check_command_for_user:
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


# реакция пользователя на заказ
@router.callback_query(F.data.startswith('ready'))
async def process_pass_edit_service(callback: CallbackQuery, bot: Bot) -> None:
    logging.info(f'process_pass_edit_service: {callback.message.chat.id}')
    ready = callback.data.split('_')[1]
    id_order = callback.data.split('_')[2]
    # пользователь согласился выполнить заказ
    if ready == 'yes':
        # получаем информацию о заказе
        info_orders = get_row_orders_id(int(id_order))

        # требуемое количество исполнителей
        count_players = info_orders[0][4]
        # количество исполнителей готовых выполнить заказ len(players)
        if info_orders[0][5] == 'players':
            players = []
        else:
            players = info_orders[0][5].split(',')
        # если количество исполнителей для услуги меньше готовых ее выполнить
        if count_players > len(players):
            # добавляем пользователя в список
            players.append(f'{callback.from_user.username}.{callback.message.chat.id}')
            # объединяем в строку
            new_players = ','.join(players)
            # обновляем заказ
            update_list_players(new_players, int(id_order))
            await callback.message.answer(text=f'Отлично вы в команде!')
            # если пользователь был последним в списке
            if not count_players - len(players):
                info_orders = get_row_orders_id(int(id_order))
                list_sendler = info_orders[0][6].split(',')
                print(list_sendler)
                for row_sendler in list_sendler:
                    chat_id = row_sendler.split('_')[0]
                    message_id = row_sendler.split('_')[1]
                    await bot.delete_message(chat_id=chat_id,
                                             message_id=message_id)
                await asyncio.sleep(5)
                list_players = info_orders[0][5].split(',')
                list_chat_id_player = [row.split('.')[1] for row in list_players]
                number_random = random.choice(list_chat_id_player)
                await bot.send_message(chat_id=int(number_random),
                                       text='Отправьте отчет о проделанной работе',
                                       reply_markup=keyboard_send_report())
    else:
        await callback.message.answer(text=f'Жаль, выполнит заказ другой')

@router.callback_query(F.data == 'report')
async def process_send_report(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_send_report: {callback.message.chat.id}')
    await callback.message.answer(text='Отправь отчет о проделанной работе')
    await state.set_state(User.report)


@router.message(F.text, StateFilter(User.report))
async def get_token_user(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'get_token_user: {message.chat.id}')
    try:
        chat_id = get_channel()[0][0]
        print(chat_id)
        await bot.send_message(chat_id=chat_id, text=f'{message.text}')
    except:
        await message.answer(text=f'Отчет не отправлен')
