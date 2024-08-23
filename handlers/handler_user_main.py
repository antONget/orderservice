import random

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
import keyboards.keyboard_user_main as kb
from aiogram.types import CallbackQuery
import requests
import asyncio
import logging
from config_data.config import Config, load_config
import database.requests as rq


router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class User(StatesGroup):
    get_token = State()
    auth_token = State()
    report1 = State()
    report2 = State()


def get_telegram_user(user_id: int, bot_token: str):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    return response.json()


# запуск бота пользователем /start

@router.message(CommandStart(), F.chat.type == "private")
async def process_start_command_user(message: Message, state: FSMContext) -> None:
    """
    Нажатие или ввод команды /start пользователем не являющимся админом
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_start_command_user: {message.chat.id}')
    if not await rq.get_user_tg_id(tg_id=message.chat.id):
        await message.answer(text='Для авторизации в боте пришлите токен который вам отправил администратор')
        await state.set_state(User.get_token)
    else:
        await message.answer(text='Вы авторизованы в боте, и можете получать заказы на услуги',
                             reply_markup=kb.keyboards_main_user())


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
    if await rq.check_token(token=message.text):
        if message.from_user.username:
            username = message.from_user.username
        else:
            username = 'None'
        await rq.add_user(telegram_id=message.chat.id, username=username, token=message.text)
        await message.answer(text='Вы добавлены',
                             reply_markup=kb.keyboards_main_user())
        list_admin = await rq.get_list_admins(is_admin=1)
        for admin in list_admin:
            result = get_telegram_user(user_id=admin.telegram_id, bot_token=config.tg_bot.token)
            if 'result' in result:
                try:
                    await bot.send_message(chat_id=admin.telegram_id,
                                           text=f'Пользователь @{message.from_user.username} авторизован')
                except:
                    pass
        await state.set_state(default_state)
    else:
        await message.answer(text='TOKEN не прошел верификацию. Попробуйте с другим токеном')


# реакция пользователя на заказ
@router.callback_query(F.data.startswith('ready_'))
async def process_pass_edit_service(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    """
    Согласие на выполнение заказа, нажата кнопка "ДА"/"НЕТ"
    проверка на занятость пользователя в других заказах
    :param callback: ready_yes_{id_order}
    :param bot:
    :param state:
    :return:
    """
    logging.info(f'process_pass_edit_service: {callback.message.chat.id}')
    # проверяем занятость пользователя
    # !!! TypeError: 'NoneType' object is not subscriptable
    user_info = await rq.get_user_tg_id(tg_id=callback.message.chat.id)
    order_id = int(callback.data.split('_')[2])
    order_info = await rq.get_order_id(order_id=order_id)
    if user_info.is_busy:
        await callback.answer(text='Вы не можете брать другие заказы, пока не будет получен отчет!',
                              show_alert=True)
        return

    else:
        data = await state.get_data()
        executor_info = await rq.get_executor_tg_id_order_id(order_id=order_id,
                                                             tg_id=callback.message.chat.id)
        # если исполнитель есть и он еще не брал заказ
        if executor_info: # !!! KeyError: 6517086173, KeyError: 6669623091, KeyError: 6669623091, KeyError: 6915946557, KeyError: 5086232463
            ready = callback.data.split('_')[1]
            # пользователь согласился выполнить заказ
            if ready == 'yes':
                # количество исполнителей согласных выполнить заказ
                count_executor = len([executor for executor in
                                      await rq.get_executors_status_order_id(order_id=order_id,
                                                                             status=rq.ExecutorStatus.done)])
                # есть ли место в заказе
                if count_executor >= order_info.count_people:
                    await callback.answer(text='Вы опоздали, заказ собран!'
                                               ' Если кто-то попросит замену у вас будет шанс!')
                    return
                else:
                    # проверяем список с заменами, которые еще не закрыты
                    change_list = await rq.get_executors_status_order_id(order_id=order_id,
                                                                         status=rq.ExecutorStatus.change)
                    for change_executor in change_list:
                        if change_executor.change_id == 0:
                            change_user = await rq.get_user_tg_id(change_executor.tg_id)
                            # список админов
                            list_admin = await rq.get_list_admins(is_admin=1)
                            # информируем админов о произведенной замене
                            for admin in list_admin:
                                result = get_telegram_user(user_id=admin.telegram_id, bot_token=config.tg_bot.token)
                                if 'result' in result:
                                    await bot.send_message(chat_id=admin.telegram_id,
                                                           text=f'Пользователь @{user_info.username} взял заказ'
                                                                f' №{order_info.id} вместо @{change_user.username}')
                            await rq.set_executors_change_tg_id_order_id(order_id=order_id,
                                                                         tg_id=change_executor.tg_id,
                                                                         change_id=callback.message.chat.id)
                            # прерываем цикл так производим одну замену
                            break
                    # устанавливаем исполнителю, что он готов выполнить заказ
                    await rq.set_executors_status_tg_id_order_id(order_id=order_id,
                                                                 tg_id=callback.message.chat.id,
                                                                 status=rq.ExecutorStatus.done)
                    await rq.set_busy_id(telegram_id=callback.message.chat.id, busy=1)

                    # обновляем клавиатуру с ДА на ЗАМЕНИТЬ
                    await callback.message.edit_reply_markup(reply_markup=kb.keyboard_change_player(id_order=order_id))
                    await callback.answer(text=f'Отлично вы взяли заказ! '
                                               f'{count_executor + 1}/{order_info.count_people}\n'
                                               f'Вы не можете брать другие заказы, пока не будет получен отчет!',
                                          show_alert=True)
                    executors_done = [executor for executor in
                                          await rq.get_executors_status_order_id(order_id=order_id,
                                                                                 status=rq.ExecutorStatus.done)]
                    # если пользователь был последним в списке (пулле) требуемых исполнителей
                    if len(executors_done) == order_info.count_people:
                        # удаляем сообщения с заказами у пользователей которые не готовы выполнять заказ
                        executors_none = await rq.get_executors_status_order_id(order_id=order_id,
                                                                                status=rq.ExecutorStatus.none)
                        for none_executor in executors_none:
                            await rq.delete_executor(tg_id=none_executor.tg_id, order_id=order_id)
                            try:
                                await bot.delete_message(chat_id=none_executor.tg_id,
                                                         message_id=none_executor.message_id)
                            except:
                                pass
                        # сообщение для информирования об исполнителях
                        text_player = 'Выполняют:\n'
                        for executor in executors_done:
                            user_info = await rq.get_user_tg_id(tg_id=executor.tg_id)
                            text_player += f'@{user_info.username}\n'

                        # отправляем в канал и беседу сообщение об исполнителях выполняющих заказ
                        list_chat_id = await rq.get_channels()
                        for chat in list_chat_id:
                            result = get_telegram_user(user_id=chat.channel_id, bot_token=config.tg_bot.token)
                            if 'result' in result:
                                try:
                                    await bot.send_message(chat_id=chat.channel_id,
                                                           text=f'Заказ № {order_info.id} в работе!\n\n'
                                                                f'{text_player}')
                                except:
                                    pass
                        # информируем админа о том, что пользователи для выполнения заказа собраны
                        list_admin = await rq.get_list_admins(is_admin=1)
                        for admin in list_admin:
                            result = get_telegram_user(user_id=admin.telegram_id, bot_token=config.tg_bot.token)
                            if 'result' in result:
                                await bot.send_message(chat_id=admin.telegram_id,
                                                       text=f'Заказ № {order_info.id} в работе!\n\n'
                                                            f'{text_player}')
                        change_list = await rq.get_executors_status_order_id(order_id=order_id,
                                                                             status=rq.ExecutorStatus.change)
                        # формируем информацию о заменах
                        text_change_user = ''
                        for change_user in change_list:
                            user_ch = await rq.get_user_tg_id(tg_id=change_user.tg_id)
                            user_ex = await rq.get_user_tg_id(tg_id=change_user.change_id)
                            text_change_user += f'Пользователь @{user_ch.username} заменен на @{user_ex.username}\n'
                        # производим рассылку информации о заменах в канал и беседу
                        if list_chat_id and text_change_user != '':
                            for chat in list_chat_id:
                                result = get_telegram_user(user_id=chat.channel_id, bot_token=config.tg_bot.token)
                                if 'result' in result:
                                    await bot.send_message(chat_id=chat.channel_id,
                                                           text=f'Замена в заказе №{order_info.id}\n\n'+text_change_user)
                        await asyncio.sleep(1)
                        # добавляем кнопку отчета исполнителям случайным образом
                        try:
                            number_random = random.choice(executors_done)
                            await bot.edit_message_reply_markup(chat_id=number_random.tg_id,
                                                                message_id=number_random.message_id,
                                                                reply_markup=kb.keyboard_send_report(id_order=order_id))
                        # если случайно не удалось добавить то пытаемся добавить одному из исполнителей
                        except:
                            for done in executors_done:
                                try:
                                    await bot.edit_message_reply_markup(chat_id=done.tg_id,
                                                                        message_id=done.message_id,
                                                                        reply_markup=kb.keyboard_send_report(
                                                                            id_order=order_id))
                                    break
                                except:
                                    await bot.send_message(chat_id=config.tg_bot.support_id,
                                                           text=f'ERRROR!!!\nКнопка отчет к заказу № {order_info.id} не добавлена')

            # пользователь отказался от выполнения заказа
            else:
                await callback.message.answer(text=f'Жаль, выполнит заказ другой')
                await rq.set_executors_status_tg_id_order_id(order_id=order_id,
                                                             tg_id=callback.message.chat.id,
                                                             status=rq.ExecutorStatus.cancel)
                try:
                    await bot.delete_message(chat_id=callback.message.chat.id,
                                             message_id=executor_info.message_id)
                except:
                    pass


@router.callback_query(F.data.startswith('report_'))
async def process_send_report(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Предложение отправить отчет о выполненном заказе
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_send_report: {callback.message.chat.id}')
    await callback.message.answer(text='Отправьте отчет о проделанной работе',
                                  reply_markup=kb.keyboard_confirm_report())
    await state.update_data(id_order=int(callback.data.split('_')[1]))
    await state.update_data(id_message_order=callback.message.message_id)
    await callback.answer()

@router.callback_query(F.data == 'noreport')
async def process_report_no(callback: CallbackQuery, bot: Bot) -> None:
    """
    Отмена отправки отчета
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'process_report_no: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)


@router.callback_query(F.data == 'yesreport')
async def process_report_yes(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Отправка отчета по заказу
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_report_yes: {callback.message.chat.id}')
    await callback.message.edit_text(text='Какая выкладка у клиента?',
                                     reply_markup=None)
    data = await state.get_data()
    info_order = await rq.get_order_id(order_id=data['id_order'])
    executor_user = await rq.get_executor_tg_id_order_id(tg_id=callback.message.chat.id, order_id=info_order.id)
    executor_done = await rq.get_executors_status_order_id(order_id=info_order.id, status=rq.ExecutorStatus.done)
    for executor in executor_done:
        data_statistic = {"tg_id": executor.tg_id,
                          "cost_order": info_order.cost_services,
                          "order_id": info_order.id}
        await rq.add_statistic(data=data_statistic)
        try:
            await bot.delete_message(chat_id=executor.tg_id,
                                     message_id=executor.message_id)
        except:
            pass
        await rq.set_busy_id(telegram_id=executor.tg_id, busy=0)
    await state.set_state(User.report1)


@router.message(F.text, StateFilter(User.report1))
async def process_send_report1(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_send_report1: {message.chat.id}')
    await state.update_data(report1=message.text)
    await message.answer(text='Что было выдано на 1-й карте по завершению сопровождения?')
    await state.set_state(User.report2)
    # !!! TelegramBadRequest: Telegram server says - Bad Request: message to delete not found
    # await bot.delete_message(chat_id=message.chat.id,
    #                          message_id=message.message_id)
    # await bot.delete_message(chat_id=message.chat.id,
    #                          message_id=message.message_id-1)


@router.message(F.text, StateFilter(User.report2))
async def process_send_report2(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_send_report2: {message.chat.id}')
    await state.update_data(report2=message.text)
    data = await state.get_data()
    info_order = await rq.get_order_id(data['id_order'])
    title_order = info_order.title_services
    cost_order = info_order.cost_services
    executor_done = await rq.get_executors_status_order_id(order_id=info_order.id, status=rq.ExecutorStatus.done)
    # проходим по всем исполнителям заказа
    str_player = ''
    for executor in executor_done:
        result = get_telegram_user(user_id=executor.tg_id, bot_token=config.tg_bot.token)
        if 'result' in result:
            await bot.send_message(chat_id=executor.tg_id,
                                   text=f'<b>ОТЧЁТ по заказу № {data["id_order"]}: {title_order}</b> отправлен!')
        user_info = await rq.get_user_tg_id(executor.tg_id)
        str_player += f'@{user_info.username}\n'
        await rq.set_executors_status_tg_id_order_id(order_id=info_order.id,
                                                     tg_id=executor.tg_id,
                                                     status=rq.ExecutorStatus.complete)

    await rq.set_order_report(order_id=info_order.id,
                              report=f'Выкладка: {data["report1"]} Выдано: {data["report2"]}')
    list_chat_id = await rq.get_channels()
    for chat in list_chat_id:
        try:
            await bot.send_message(chat_id=chat.channel_id,
                                   text=f'<b>ОТЧЁТ № {data["id_order"]}</b>\n\n'
                                        f'<i>{title_order}</i>\n'
                                        f'<b>Выполнили:</b>\n'
                                        f'{str_player}\n\n'
                                        f'<b>Выкладка:</b> {data["report1"]}\n'
                                        f'<b>Выдано:</b> {data["report2"]}\n'
                                        f'<b>ID:</b> {info_order.comment}',
                                   parse_mode='html')
        except:
            pass
    await state.set_state(default_state)


@router.message(F.text == 'Баланс')
async def process_get_balans(message: Message) -> None:
    """
    Получаем сумму выполненных заказов
    :param message:
    :return:
    """
    logging.info(f'process_get_balans: {message.chat.id}')
    list_statistic = await rq.get_statistic_tg_id(tg_id=message.chat.id)

    if list_statistic:
        total = 0
        for item in list_statistic:
            total += item.cost_order
        # !!! TelegramNetworkError: HTTP Client says - Request timeout error
        await message.answer(text=f'Ваш баланс: {total}')
    else:
        await message.answer(text='Данные для статистики отсутствуют')


# ЗАМЕНА
@router.callback_query(F.data.startswith('change_player_'))
async def process_confirm_change_player(callback: CallbackQuery) -> None:
    logging.info(f'process_confirm_change_player: {callback.message.chat.id}')
    id_order = callback.data.split('_')[2]
    await callback.message.answer(text=f'Вы точно хотите отменить заказ?',
                                  reply_markup=kb.keyboard_confirm_change(id_order=id_order))
    await callback.answer()


@router.callback_query(F.data.startswith('nochange'))
async def process_confirm_change_player(callback: CallbackQuery, bot: Bot) -> None:
    logging.info(f'process_confirm_change_player: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)


@router.callback_query(F.data.startswith('yeschange'))
async def process_change_player(callback: CallbackQuery, bot: Bot) -> None:
    """
    Подтверждение замены в заказе
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'process_change_player: {callback.message.chat.id}')
    # обновляем занятость
    await rq.set_busy_id(telegram_id=callback.message.chat.id, busy=0)
    # получаем номер заказа
    id_order = int(callback.data.split('_')[1])
    # информация о заказе
    info_executor = await rq.get_executor_tg_id_order_id(order_id=id_order,
                                                         tg_id=callback.message.chat.id)
    await rq.set_executors_status_tg_id_order_id(order_id=id_order,
                                                 tg_id=info_executor.tg_id,
                                                 status=rq.ExecutorStatus.change)
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=info_executor.message_id)
    executor_done = [executor for executor in
                     await rq.get_executors_status_order_id(order_id=id_order,
                                                            status=rq.ExecutorStatus.done)]
    # если остались исполнители
    if executor_done:
        for executor in executor_done:
            try:
                await bot.edit_message_reply_markup(chat_id=executor.tg_id,
                                                    message_id=executor.message_id,
                                                    reply_markup=kb.keyboard_change_player(id_order=id_order))
            except:
                pass

    # информируем администраторов о замене
    list_admin = await rq.get_list_admins(is_admin=1)
    for admin in list_admin:
        result = get_telegram_user(user_id=admin.telegram_id, bot_token=config.tg_bot.token)
        if 'result' in result:
            try:
                await bot.send_message(chat_id=admin.telegram_id,
                                       text=f'Пользователь @{callback.from_user.username} отказался'
                                            f' от заказа № {id_order}')
            except:
                pass
    # если до замены заказ был собран
    order_info = await rq.get_order_id(order_id=id_order)
    if (len(executor_done) + 1) == order_info.count_people:
        # список пользователей не админов
        list_sandler = await rq.get_all_users_not_admin()
        list_mailing = []
        # обновленная информация о заказе
        info_order = await rq.get_order_id(order_id=id_order)
        # информация об услуге
        service_info = await rq.get_service_id(service_id=info_order.service_id)
        executor_change = await rq.get_executors_status_order_id(order_id=id_order, status=rq.ExecutorStatus.change)
        list_executor_change = []
        for executor in executor_change:
            list_executor_change.append(executor.tg_id)
        list_executor_done = []
        for executor in executor_done:
            list_executor_done.append(executor.tg_id)
        # производим рассылку заказа
        for user in list_sandler:
            if user.telegram_id in list_executor_done or user.telegram_id in list_executor_change:
                continue
            result = get_telegram_user(user_id=user.telegram_id, bot_token=config.tg_bot.token)
            if 'result' in result:

                if not service_info.picture_services == 'None':
                    msg = await bot.send_photo(photo=service_info.picture_services,
                                               chat_id=user.telegram_id,
                                               caption=f'Появился заказ № {order_info.id} на : {service_info.title_services}.\n'
                                                       f'Стоимость {service_info.cost_services}\n'
                                                       f'Комментарий <code>{order_info.comment}</code>\n'
                                                       f'Готовы выполнить?',
                                               reply_markup=kb.keyboard_ready_player(id_order=id_order))
                else:
                    msg = await bot.send_message(chat_id=user.telegram_id,
                                                 text=f'Появился заказ № {order_info.id} на : {service_info.title_services}.\n'
                                                      f'Стоимость {service_info.cost_services}\n'
                                                      f'Комментарий <code>{order_info.comment}</code>\n'
                                                      f'Готовы выполнить?',
                                                 reply_markup=kb.keyboard_ready_player(id_order=id_order))
                # добавляем пользователя в БД исполнителей заказа
                data_executor = {"tg_id": user.telegram_id,
                                 "id_order": info_order.id,
                                 "cost_order": info_order.cost_services,
                                 "status_executor": rq.ExecutorStatus.none,
                                 "message_id": msg.message_id}
                await rq.add_executor(data=data_executor)
    await callback.answer()
    try:
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
    except:
        pass


