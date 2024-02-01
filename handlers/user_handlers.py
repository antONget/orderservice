import random

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from keyboards.keyboards import *
from aiogram.types import CallbackQuery
import json
import asyncio
from module.data_base import check_command_for_admins, table_users, check_command_for_user, get_row_orders_id, \
    update_list_players, get_channel, get_list_admin, get_busy_id, set_busy_id, update_report
import logging
from config_data.config import Config, load_config
from module.data_base import check_token

router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class User(StatesGroup):
    get_token = State()
    auth_token = State()
    report1 = State()
    report2 = State()


user_dict1 = {}

# запуск бота пользователем /start
@router.message(CommandStart())
async def process_start_command_user(message: Message, state: FSMContext) -> None:
    table_users()
    logging.info(f'process_start_command_user: {message.chat.id}')
    if not check_command_for_user(message):
        await message.answer(text='Для авторизации в боте пришлите токен который вам отправил администратор')
        await state.set_state(User.get_token)
    else:
        await message.answer(text='Вы авторизованы в боте, и можете получать заказы на услуги')


# проверяем TOKEN
@router.message(F.text, StateFilter(User.get_token))
async def get_token_user(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'get_token_user: {message.chat.id}')
    if check_token(message):
        await message.answer(text='Вы добавлены')
        list_admin = get_list_admin()
        for row in list_admin:
            await bot.send_message(chat_id=row[0],
                                   text=f'Пользователь @{message.from_user.username} авторизован')
        # await bot.send_message(chat_id=config.tg_bot.admin_ids,
        #                        text=f'Пользователь @{message.from_user.username} авторизован')
        await state.set_state(User.auth_token)
    else:
        await message.answer(text='TOKEN не прошел верификацию. Попробуйте с другим токеном')


# реакция пользователя на заказ
@router.callback_query(F.data.startswith('ready'))
async def process_pass_edit_service(callback: CallbackQuery, bot: Bot) -> None:
    logging.info(f'process_pass_edit_service: {callback.message.chat.id}')
    # проверяем звнятость пользователя
    # print(get_busy_id(callback.message.chat.id))
    if get_busy_id(callback.message.chat.id):
        await callback.message.answer(text='Вы не можете брать другие заказы, пока не будет получен отчет!')
    else:
        set_busy_id(1, callback.message.chat.id)
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
                await callback.message.answer(text=f'Отлично вы взяли заказ!\n'
                                                   f'Вы не можете брать другие заказы, пока не будет получен отчет!')
                # если пользователь был последним в списке
                if not count_players - len(players):
                    # получаем информацию о заказе
                    info_orders = get_row_orders_id(int(id_order))
                    # список рассылки сообщения с заказом
                    list_sendler = info_orders[0][6].split(',')
                    print(list_sendler)
                    for row_sendler in list_sendler:
                        # id чата и сообщения для удаления
                        chat_id = row_sendler.split('_')[0]
                        message_id = row_sendler.split('_')[1]
                        # получаем список id исполнителей [@username.id_telegram.id_message]
                        list_players = [row.split('.')[1] for row in info_orders[0][5].split(',')]
                        # если пользователь не является исполнителем то удаляем у него заказ
                        if chat_id not in list_players:
                            await bot.delete_message(chat_id=chat_id,
                                                     message_id=message_id)
                    list_admin = get_list_admin()
                    print(list_admin)
                    for admin in list_admin:
                        await bot.send_message(chat_id=admin[0],
                                               text=f'Заказ № {id_order} в работе!')
                    await asyncio.sleep(5)
                    list_players = info_orders[0][5].split(',')
                    list_chat_id_player = [row.split('.')[1] for row in list_players]
                    number_random = random.choice(list_chat_id_player)
                    await bot.send_message(chat_id=int(number_random),
                                           text='Отправьте отчет о проделанной работе',
                                           reply_markup=keyboard_send_report(id_order))
        else:
            await callback.message.answer(text=f'Жаль, выполнит заказ другой')


@router.callback_query(F.data.startswith('report'))
async def process_send_report(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_send_report: {callback.message.chat.id}')
    await callback.message.edit_text(text='Какая выкладка у клиента?')
    await state.update_data(id_order=callback.data.split('_')[1])
    await state.set_state(User.report1)


@router.message(F.text, StateFilter(User.report1))
async def process_send_report1(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_send_report1: {message.chat.id}')
    await state.update_data(report1=message.text)
    await message.answer(text='Что было выдано на 1-й карте по завершению сопровождения?')
    await state.set_state(User.report2)


@router.message(F.text, StateFilter(User.report2))
async def process_send_report2(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_send_report2: {message.chat.id}')
    await state.update_data(report2=message.text)
    user_dict1[message.chat.id] = await state.get_data()
    info_orders = get_row_orders_id(int(user_dict1[message.chat.id]['id_order']))
    print(info_orders)
    title_order = info_orders[0][1]
    cost_order = info_orders[0][2]
    # список рассылки
    list_mailer = info_orders[0][6].split(',')
    total = info_orders[0][2] * info_orders[0][4]
    # получаем username иполнителей
    list_players = []
    # проходим по всем исполнителям заказа
    for row in info_orders[0][5].split(','):
        list_players.append(f'@{row.split(".")[0]} ({cost_order})')
        await bot.send_message(chat_id=int(row.split(".")[1]),
                               text=f'<b>ОТЧЁТ по заказу {user_dict1[message.chat.id]["id_order"]}: {title_order}</b> отправлен!')
        # освобождаем исполнителя
        set_busy_id(0, int(row.split(".")[1]))
        # удаляем заказ у исполнителей list_mailer [id, message_id]
        for iduser_idmessage in list_mailer:
            if int(iduser_idmessage.split('_')[0]) == int(row.split(".")[1]):
                await bot.delete_message(chat_id=int(row.split(".")[1]),
                                         message_id=int(iduser_idmessage.split('_')[1]))
        # for player in info_orders[0][5].split(','):
        #     await bot.delete_message(chat_id=int(row.split(".")[1]),
        #                              message_id=int(row.split(".")[2]))
    update_report(report=f'Выкладка: {user_dict1[message.chat.id]["report1"]} Выдано: {user_dict1[message.chat.id]["report2"]}',
                  id_orders=int(user_dict1[message.chat.id]["id_order"]))
    str_player = '\n'.join(list_players)
    # try:
    list_chat_id = get_channel()
    print(list_chat_id)
    # chat_id=config.tg_bot.channel_id
    # print(chat_id)
    for chat_id in list_chat_id:
        await bot.send_message(chat_id=int(chat_id[0]),
                               text=f'<b>ОТЧЁТ № {user_dict1[message.chat.id]["id_order"]}</b>\n\n'
                                    f'<b>Выполнили:</b>\n'
                                    f'{str_player}\n\n'
                                    f'<b>Выкладка:</b> {user_dict1[message.chat.id]["report1"]}\n'
                                    f'<b>Выдано:</b> {user_dict1[message.chat.id]["report2"]}\n',
                               parse_mode='html')
    # except:
    # await message.answer(text=f'<b>ОТЧЁТ по услуге: {title_order}</b>\n\n'
    #                           f'<b>Выполнили: </b>\n'
    #                           f'{str_player}\n\n'
    #                           f'<b>Выкладка:</b> {user_dict1[message.chat.id]["report1"]}\n'
    #                           f'<b>Выдано:</b> {user_dict1[message.chat.id]["report2"]}\n')
    await state.set_state(default_state)