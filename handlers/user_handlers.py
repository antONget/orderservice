import random

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from keyboards.keyboards import keyboard_send_report, keyboards_main_user, keyboard_change_player, \
    keyboard_confirm_report, keyboard_ready_player, keyboard_confirm_change
from aiogram.types import CallbackQuery

import asyncio
from module.data_base import check_command_for_admins, table_users, check_command_for_user, get_row_orders_id, \
    update_list_players, get_channel, get_list_admin, get_busy_id, set_busy_id, update_report, add_statistic, \
    select_alldata_statistic, table_statistic, update_list_refuses, get_list_users_notadmin, get_row_services, \
    update_list_sendlers, get_user
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
    """
    Нажатие или ввод команды /start пользователем не являющимся админом
    :param message:
    :param state:
    :return:
    """
    table_users()
    table_statistic()
    logging.info(f'process_start_command_user: {message.chat.id}')
    if not check_command_for_user(message):
        await message.answer(text='Для авторизации в боте пришлите токен который вам отправил администратор')
        await state.set_state(User.get_token)
    else:
        await message.answer(text='Вы авторизованы в боте, и можете получать заказы на услуги',
                             reply_markup=keyboards_main_user())


# проверяем TOKEN
@router.message(F.text, StateFilter(User.get_token))
async def get_token_user(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Валидация TOKEN введенного пользователем, добавление его в базу и информирование списка администраторов
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_token_user: {message.chat.id}')
    if check_token(message):
        await message.answer(text='Вы добавлены',
                             reply_markup=keyboards_main_user())
        list_admin = get_list_admin()
        for row in list_admin:
            await bot.send_message(chat_id=row[0],
                                   text=f'Пользователь @{message.from_user.username} авторизован')
        await state.set_state(default_state)
    else:
        await message.answer(text='TOKEN не прошел верификацию. Попробуйте с другим токеном')


# реакция пользователя на заказ
@router.callback_query(F.data.startswith('ready'))
async def process_pass_edit_service(callback: CallbackQuery, bot: Bot) -> None:
    """
    Согласие на выполнение заказа, нажата кнопка "ДА"
    проверка на занятость пользователя в других заказах
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'process_pass_edit_service: {callback.message.chat.id}')
    # проверяем занятость пользователя
    if get_busy_id(callback.message.chat.id):
        await callback.answer(text='Вы не можете брать другие заказы, пока не будет получен отчет!',
                              show_alert=True)
    else:
        set_busy_id(1, callback.message.chat.id)
        ready = callback.data.split('_')[1]
        id_order = callback.data.split('_')[2]
        # пользователь согласился выполнить заказ
        if ready == 'yes':
            # получаем информацию о заказе
            info_orders = get_row_orders_id(int(id_order))
            # список отказавшихся от выполнения заказа @username.telegram_id
            change_list = info_orders[0][7].split(',')
            logging.info(f'process_pass_edit_service:change_list {change_list}')
            # информируем администратора о замене (информируем только если в столбце замены есть данные id_id)
            for i, change_user in enumerate(change_list):
                # если первая позиция или замены не было
                if change_user == 'change' or len(change_user.split('_')) != 1:
                    print("change_user", change_user)
                # если замена была
                else:
                    # получаем строку замены
                    change_list[i] = change_user + '_' + str(callback.message.chat.id)
                    # список админов
                    list_admin = get_list_admin()
                    logging.info(f'process_pass_edit_service:list_admin {list_admin}')
                    # информируем админов о произведенной замене
                    for admin in list_admin:
                        await bot.send_message(chat_id=admin[0],
                                               text=f'Пользователь @{callback.from_user.username} взял заказ'
                                                    f' №{id_order} вместо @{get_user(int(change_user))[0]}')
            # формируем новый список замен
            change_list_str = ','.join(change_list)
            # обновляем список замен в базе
            update_list_refuses(list_refuses=change_list_str, id_orders=int(id_order))
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
                # объединяем в строку пользователей согласившихся выполнять заказ
                new_players = ','.join(players)
                # обновляем заказ в базе
                update_list_players(new_players, int(id_order))
                # info_order = get_row_orders_id(int(id_order))
                # list_message = info_order[0][6].split(',')
                # for mes in list_message:
                #     if mes.split('_')[0] == str(callback.message.chat.id):
                # обновляем клавиатуру с ДА на ЗАМЕНИТЬ
                await callback.message.edit_reply_markup(reply_markup=keyboard_change_player(id_order))
                await callback.answer('Отлично вы взяли заказ!\n'
                                      'Вы не можете брать другие заказы, пока не будет получен отчет!',
                                      show_alert=True)

                # если пользователь был последним в списке
                if not count_players - len(players):
                    # получаем информацию о заказе
                    info_orders = get_row_orders_id(int(id_order))
                    # список рассылки сообщения с заказом
                    list_sendler = info_orders[0][6].split(',')
                    print(list_sendler)
                    list_sendler_del = list_sendler.copy()
                    # удаляем сообщения
                    for i, row_sendler in enumerate(list_sendler):
                        # id чата и сообщения для удаления
                        chat_id = row_sendler.split('_')[0]
                        message_id = row_sendler.split('_')[1]

                        # получаем список id исполнителей [@username.id_telegram.id_message]
                        list_players = [row.split('.')[1] for row in info_orders[0][5].split(',')]
                        # если пользователь не является исполнителем, то удаляем у него заказ
                        if chat_id not in list_players:
                            await bot.delete_message(chat_id=chat_id,
                                                     message_id=message_id)
                            list_sendler_del.remove(row_sendler)
                    list_mailing_str = ','.join(list_sendler_del)
                    update_list_sendlers(list_mailing_str=list_mailing_str, id_orders=int(id_order))
                    # информируем админа о том, что пользователи для выполнения заказа собраны
                    list_admin = get_list_admin()
                    for admin in list_admin:
                        await bot.send_message(chat_id=admin[0],
                                               text=f'Заказ № {id_order} в работе!')
                    # отправляем информацию в канал и группу
                    list_chat_id = get_channel()
                    # список отказавшихся от выполнения заказа @username.telegram_id
                    change_list = info_orders[0][7].split(',')
                    # формируем информацию о заменах
                    text_change_user = ''
                    for i, change_user in enumerate(change_list):
                        if change_user == 'change' or len(change_user.split('_')) < 2:
                            pass
                        else:
                            text_change_user += f'Пользователь @{get_user(int(change_user.split("_")[0]))[0]} ' \
                                                f'заменен на @{get_user(int(change_user.split("_")[1]))[0]}\n'
                    if list_chat_id and text_change_user != '':
                        for chat_id in list_chat_id:
                            await bot.send_message(chat_id=int(chat_id),
                                                   text=f'Замена в заказе №{id_order}\n\n'+text_change_user)
                    await asyncio.sleep(1)
                    list_players = info_orders[0][5].split(',')
                    list_chat_id_player = [row.split('.')[1] for row in list_players]
                    logging.info(f'process_pass_edit_service:list_chat_id_player {list_chat_id_player}')
                    number_random = random.choice(list_chat_id_player)
                    logging.info(f'process_pass_edit_service:number_random {number_random}')
                    message_sendler = 0
                    for info_message_sendler in list_sendler_del:
                        if info_message_sendler.split('_')[0] == str(number_random):
                            message_sendler = info_message_sendler.split('_')[1]
                    await bot.edit_message_reply_markup(chat_id=int(number_random),
                                                        message_id=int(message_sendler),
                                                        reply_markup=keyboard_send_report(id_order))
        else:
            await callback.message.answer(text=f'Жаль, выполнит заказ другой')


@router.callback_query(F.data.startswith('report'))
async def process_send_report(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_send_report: {callback.message.chat.id}')
    logging.info(f'process_send_report: {callback.message.message_id}')
    # info_orders = get_row_orders_id(int(callback.data.split('_')[1]))
    # change_list = info_orders[0][7].split(',')
    # flag = 1
    # for change in change_list:
    #
    #     if change == 'change' or len(change.split('_')) == 1:
    #         print("change:::", change, len(change.split('_')))
    #     else:
    #         change_user = change.split('_')[1]
    #         if str(callback.message.chat.id) == change_user:
    #             await bot.delete_message(chat_id=callback.message.chat.id,
    #                                      message_id=callback.message.message_id)
    #             flag = 0
    # if flag:
    await callback.message.answer(text='Отправьте отчет о проделанной работе',
                                  reply_markup=keyboard_confirm_report())
    await state.update_data(id_order=callback.data.split('_')[1])
    await state.update_data(id_message_order=callback.message.message_id)


@router.callback_query(F.data == 'noreport')
async def process_report_no(callback: CallbackQuery, bot: Bot) -> None:
    logging.info(f'process_report_no: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)




@router.callback_query(F.data == 'yesreport')
async def process_report_yes(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_report_yes: {callback.message.chat.id}')
    await callback.message.edit_text(text='Какая выкладка у клиента?')
    user_dict1[callback.message.chat.id] = await state.get_data()
    info_order = get_row_orders_id(user_dict1[callback.message.chat.id]['id_order'])
    print(info_order)
    add_statistic(cost_services=info_order[0][2], count_people=info_order[0][4], players=info_order[0][5])

    # await bot.delete_message(chat_id=callback.message.chat.id,
    #                          message_id=callback.message.message_id)
    # await bot.delete_message(chat_id=callback.message.chat.id,
    #                          message_id=user_dict1[callback.message.chat.id]['id_message_order'])
    await state.set_state(User.report1)


@router.message(F.text, StateFilter(User.report1))
async def process_send_report1(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_send_report1: {message.chat.id}')
    await state.update_data(report1=message.text)
    await message.answer(text='Что было выдано на 1-й карте по завершению сопровождения?')
    await state.set_state(User.report2)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id-1)

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
    for i, chat_id in enumerate(list_chat_id):
        if i:
            await bot.send_message(chat_id=chat_id,
                                   text=f'<b>ОТЧЁТ № {user_dict1[message.chat.id]["id_order"]}</b>\n\n'
                                        f'<i>{title_order}</i>\n'
                                        f'<b>Выполнили:</b>\n'
                                        f'{str_player}\n\n'
                                        f'<b>Выкладка:</b> {user_dict1[message.chat.id]["report1"]}\n'
                                        f'<b>Выдано:</b> {user_dict1[message.chat.id]["report2"]}\n',
                                   parse_mode='html')
        else:
            await bot.send_message(chat_id=chat_id,
                                   text=f'<b>ОТЧЁТ № {user_dict1[message.chat.id]["id_order"]}</b>\n\n'
                                        f'<i>{title_order}</i>\n'
                                        f'<b>Выполнили:</b>\n'
                                        f'{str_player}\n\n'
                                        f'<b>Выкладка:</b> {user_dict1[message.chat.id]["report1"]}\n'
                                        f'<b>Выдано:</b> {user_dict1[message.chat.id]["report2"]}\n'
                                        f'<b>ID:</b> {info_orders[0][3]}',
                                   parse_mode='html')
    # except:
    # await message.answer(text=f'<b>ОТЧЁТ по услуге: {title_order}</b>\n\n'
    #                           f'<b>Выполнили: </b>\n'
    #                           f'{str_player}\n\n'
    #                           f'<b>Выкладка:</b> {user_dict1[message.chat.id]["report1"]}\n'
    #                           f'<b>Выдано:</b> {user_dict1[message.chat.id]["report2"]}\n')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await state.set_state(default_state)


@router.message(F.text == 'Баланс')
async def process_get_balans(message: Message) -> None:
    logging.info(f'process_get_balans: {message.chat.id}')
    list_orders = select_alldata_statistic()

    # list_orders: id, cost, count, player[@username.telegram_id]
    if list_orders:
        total = 0
        for order in list_orders:
            list_players = order[3].split(',')
            print(order)
            for player in list_players:
                if player.split('.')[1] == str(message.chat.id):
                    print(order[1])
                    total += order[1]
        await message.answer(text=f'Ваш баланс: {total}')
    else:
        await message.answer(text='Данные для статистики отсутствуют')


# ЗАМЕНА
@router.callback_query(F.data.startswith('change_player'))
async def process_confirm_change_player(callback: CallbackQuery) -> None:
    logging.info(f'process_confirm_change_player: {callback.message.chat.id}')
    id_order = callback.data.split('_')[2]
    await callback.message.answer(text=f'Вы точо хотите отменить заказ?',
                                  reply_markup=keyboard_confirm_change(id_order))


@router.callback_query(F.data.startswith('nochange'))
async def process_confirm_change_player(callback: CallbackQuery, bot: Bot) -> None:
    logging.info(f'process_confirm_change_player: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)


@router.callback_query(F.data.startswith('yeschange'))
async def process_change_player(callback: CallbackQuery, bot: Bot) -> None:
    logging.info(f'process_change_player: {callback.message.chat.id}')
    # обновляем занятость
    set_busy_id(busy=0, telegram_id=callback.message.chat.id)
    # получаем номер заказа
    id_order = callback.data.split('_')[1]
    # информация о заказе
    info_order = get_row_orders_id(int(id_order))
    print(info_order)
    # получаем список рассылки и удаляем пользователя из списка рассылки
    list_message = info_order[0][6].split(',')
    for mes in list_message:
        if mes.split('_')[0] == str(callback.message.chat.id):
            await bot.delete_message(chat_id=callback.message.chat.id,
                                     message_id=int(mes.split('_')[1]))
    # получаем список отказавшихся
    list_refuses = info_order[0][7].split(',')
    # добавляем пользователя в список отказавшихся и обновляем БД
    list_refuses.append(str(callback.message.chat.id))
    list_refuses_str = ','.join(list_refuses)
    update_list_refuses(list_refuses=list_refuses_str, id_orders=int(id_order))
    # удаляем пользователя из списка исполнителей и обновляем БД
    list_players: list = info_order[0][5].split(',')
    for player in list_players:
        if str(callback.message.chat.id) == player.split('.')[1]:
            list_players.remove(player)
    if list_players:
        list_players_str = ','.join(list_players)
        update_list_players(players=list_players_str, id_orders=int(id_order))
    else:
        update_list_players(players='players', id_orders=int(id_order))
    # информируем администраторов о замене
    list_admin = get_list_admin()
    print(list_admin)
    for admin in list_admin:
        await bot.send_message(chat_id=admin[0],
                               text=f'Пользователь @{callback.from_user.username} отказался'
                                    f' от заказа №{id_order}')
    # список пользователей не админов
    list_sendler = get_list_users_notadmin()
    print(list_sendler)
    list_mailing = []
    # информация об услуге
    row_services = get_row_services(info_order[0][1])
    # обновленная информация о заказе
    info_order = get_row_orders_id(int(id_order))
    # список рассылки
    list_message = info_order[0][6].split(',')
    list_message_user_id = []
    for mes in list_message:
        list_message_user_id.append(mes.split('_')[0])
    # производим рассылку заказа
    for row in list_sendler:
        # если пользователь не суперадмин или ранее не отказался
        if str(row[0]) != str(config.tg_bot.admin_ids) and str(row[0]) not in list_refuses and str(row[0]) not in list_message_user_id:
            if not row_services[0][4] == 'None':
                msg = await bot.send_photo(photo=str(row_services[0][4]),
                                           chat_id=int(row[0]),
                                           caption=f'Появился заказ № {info_order[0][0]} на : {info_order[0][1]}.\n'
                                                   f'Стоимость: {info_order[0][2]}\n'
                                                   f'Комментарий <code>{info_order[0][3]}</code>\n'
                                                   f'Готовы выполнить?',
                                           reply_markup=keyboard_ready_player(id_order=id_order))
            else:
                msg = await bot.send_message(chat_id=int(row[0]),
                                             text=f'Появился заказ № {info_order[0][0]} на : {info_order[0][1]}.\n'
                                                  f'Стоимость: {info_order[0][2]}\n'
                                                  f'Комментарий <code>{info_order[0][3]}</code>\n'
                                                  f'Готовы выполнить?',
                                             reply_markup=keyboard_ready_player(id_order=id_order))
            iduser_idmessage = f'{row[0]}_{msg.message_id}'
            list_mailing.append(iduser_idmessage)

    list_mailing_str = ','.join(list_mailing)
    update_list_sendlers(list_mailing_str=list_mailing_str, id_orders=id_order)
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)



