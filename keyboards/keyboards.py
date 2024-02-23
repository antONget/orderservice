from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


# ГЛАВНОЕ МЕНЮ СУПЕРАДМИН
def keyboards_superadmin():
    button_1 = KeyboardButton(text='Администраторы')
    button_2 = KeyboardButton(text='Услуга')
    button_3 = KeyboardButton(text='Пользователь')
    button_4 = KeyboardButton(text='Прикрепить')
    button_5 = KeyboardButton(text='Статистика')
    button_6 = KeyboardButton(text='Сброс статистики')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2, button_3, button_4], [button_5, button_6]],
        resize_keyboard=True
    )
    return keyboard
def keyboards_superadmin_one():
    button_1 = KeyboardButton(text='Услуга')
    button_2 = KeyboardButton(text='Статистика')
    button_3 = KeyboardButton(text='>>>')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1, button_2], [button_3]],
                                   resize_keyboard=True)
    return keyboard
def keyboards_superadmin_two():
    button_1 = KeyboardButton(text='Администраторы')
    button_2 = KeyboardButton(text='Пользователь')
    button_3 = KeyboardButton(text='Прикрепить')
    button_4 = KeyboardButton(text='Сброс статистики')
    button_5 = KeyboardButton(text='<<<')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1, button_2], [button_3, button_4], [button_5]],
                                   resize_keyboard=True)
    return keyboard
# ГЛАВНОЕ МЕНЮ АДМИН
def keyboards_admin():
    button_2 = KeyboardButton(text='Услуга')
    button_3 = KeyboardButton(text='Пользователь')
    button_4 = KeyboardButton(text='Прикрепить')
    button_5 = KeyboardButton(text='Статистика')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_2, button_3, button_4], [button_5]],
        resize_keyboard=True
    )
    return keyboard
def keyboards_admin_one():
    button_1 = KeyboardButton(text='Услуга')
    button_2 = KeyboardButton(text='Статистика')
    button_3 = KeyboardButton(text='>>>')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1, button_2], [button_3]],
                                   resize_keyboard=True)
    return keyboard
def keyboards_admin_two():
    button_2 = KeyboardButton(text='Пользователь')
    button_3 = KeyboardButton(text='Прикрепить')
    button_4 = KeyboardButton(text='Сброс статистики')
    button_5 = KeyboardButton(text='<<<')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_2], [button_3, button_4], [button_5]],
                                   resize_keyboard=True)
    return keyboard

# ГЛАВНОЕ МЕНЮ ПОЛЬЗОВАТЕЛЬ
def keyboards_main_user():
    button_2 = KeyboardButton(text='Баланс')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_2]],
        resize_keyboard=True
    )
    return keyboard


# АДМИНИСТРАТОРЫ
def keyboard_edit_list_admins() -> None:
    """
    Клавиатура для редактирования списка администраторов
    :return:
    """
    button_1 = InlineKeyboardButton(text='Назначить',
                                    callback_data='add_admin')
    button_2 = InlineKeyboardButton(text='Разжаловать',
                                    callback_data='delete_admin')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


# АДМИНИСТРАТОРЫ -> Назначить
def keyboards_add_admin(list_admin, back, forward, count):
    logging.info(f'keyboards_add_admin')
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_admin)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    print(list_admin, count_users, back, forward, max_forward)
    for row in list_admin[back*count:(forward-1)*count]:
        print(row)
        text = row[1]
        button = f'adminadd_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'adminback_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'adminforward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()


# АДМИНИСТРАТОРЫ -> Назначить -> подтверждение добавления админа в список админов
def keyboard_add_list_admins() -> None:
    """
    Клавиатура для подтверждения добавления пользователя в список администраторов
    :return:
    """
    button_1 = InlineKeyboardButton(text='Назначить',
                                    callback_data='add_admin_list')
    button_2 = InlineKeyboardButton(text='Отменить',
                                    callback_data='notadd_admin_list')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


# АДМИНИСТРАТОРЫ -> Разжаловать
def keyboards_del_admin(list_admin, back, forward, count):
    logging.info(f'keyboards_del_admin')
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_admin)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    print(list_admin, count_users, back, forward, max_forward)
    for row in list_admin[back*count:(forward-1)*count]:
        print(row)
        text = row[1]
        button = f'admindel_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'admindelback_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'admindelforward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()


# АДМИНИСТРАТОРЫ -> Разжаловать -> подтверждение добавления админа в список админов
def keyboard_del_list_admins() -> None:
    """
    Клавиатура для разжалования пользователя в список администраторов
    :return:
    """
    button_1 = InlineKeyboardButton(text='Разжаловать',
                                    callback_data='del_admin_list')
    button_2 = InlineKeyboardButton(text='Отменить',
                                    callback_data='notdel_admin_list')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


# ПОЛЬЗОВАТЕЛЬ - [Добавить][Удалить]
def keyboard_edit_list_user() -> None:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Добавить',
                                    callback_data='add_user')
    button_2 = InlineKeyboardButton(text='Удалить',
                                    callback_data='delete_user')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


# ПОЛЬЗОВАТЕЛЬ -> Удалить
def keyboards_del_users(list_users, back, forward, count):
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_users)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    print(list_users, count_users, back, forward, max_forward)
    for row in list_users[back*count:(forward-1)*count]:
        print(row)
        text = row[1]
        button = f'deleteuser_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'back_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'forward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[buttons],
    )
    return kb_builder.as_markup()


# ПОЛЬЗОВАТЕЛЬ -> Удалить -> подтверждение удаления пользователя из базы
def keyboard_delete_user() -> None:
    """
    Клавиатура для редактирования списка администраторов
    :return:
    """
    button_1 = InlineKeyboardButton(text='Удалить',
                                    callback_data='del_user')
    button_2 = InlineKeyboardButton(text='Отмена',
                                    callback_data='notdel_user')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


# УСЛУГА
def keyboard_edit_select_services() -> None:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Редактировать',
                                    callback_data='edit_services')
    button_2 = InlineKeyboardButton(text='Выбрать',
                                    callback_data='select_services')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


# УСЛУГА -> Редактировать
def keyboard_edit_services() -> None:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Добавить',
                                    callback_data='append_services')
    button_2 = InlineKeyboardButton(text='Изменить',
                                    callback_data='change_services')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard



# УСЛУГА -> Добавить - изображение
def keyboard_add_picture() -> None:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Пропустить',
                                    callback_data='pass_picture')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]]
    )
    return keyboard

# УСЛУГА -> Редактировать -> Добавить
def keyboard_confirmation_append_services() -> None:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Добавить ещё',
                                    callback_data='edit_services')
    button_2 = InlineKeyboardButton(text='Закончить',
                                    callback_data='finish_services')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


# УСЛУГА -> Редактировать -> Изменить
def keyboards_edit_services(list_services, back, forward, count):
    logging.info(f'keyboards_edit_services')
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_services)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    print(list_services, count_users, back, forward, max_forward)
    for row in list_services[back*count:(forward-1)*count]:
        print(row)
        text = row[0]
        button = f'servicesedit_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'serviceseditback_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'serviceseditforward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()

# УСЛУГА -> Редактировать -> Изменить -> выбрана услуга для удаления или модификации
def keyboard_edit_list_services() -> None:
    """
    Клавиатура для редактирования списка администраторов
    :return:
    """
    button_1 = InlineKeyboardButton(text='Редактировать',
                                    callback_data='modification_services')
    button_2 = InlineKeyboardButton(text='Удалить',
                                    callback_data='delete_services')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


# УСЛУГА -> Редактировать -> Изменить -> выбрана услуга для удаления или модификации
def keyboard_pass_edit_title_services() -> None:
    """
    Клавиатура для пропуска редактирования названия услуги
    :return:
    """
    button_1 = InlineKeyboardButton(text='Пропустить',
                                    callback_data='pass_edit_service')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]],
    )
    return keyboard


# Завершение процедуры редактирование услуги
def keyboard_finish_edit_service() -> None:
    """
    Клавиатура для вовращения после редактирования
    :return:
    """
    button_1 = InlineKeyboardButton(text='Продолжить',
                                    callback_data='continue_edit_service')
    button_2 = InlineKeyboardButton(text='Завершить',
                                    callback_data='finish_edit_services')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard

# УСЛУГА -> Выбрать
def keyboards_select_services(list_services, back, forward, count):
    logging.info(f'keyboards_select_services')
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_services)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    print(list_services, count_users, back, forward, max_forward)
    for row in list_services[back*count:(forward-1)*count]:
        print(row)
        text = row[0]
        button = f'serviceselect_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'serviceselectback_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'serviceselectforward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()


# Завершение процедуры редактирование услуги
def keyboard_continue_orders() -> None:
    """
    Клавиатура для вовращения после редактирования
    :return:
    """
    button_1 = InlineKeyboardButton(text='Далее',
                                    callback_data='continue_orders')
    button_2 = InlineKeyboardButton(text='Назад',
                                    callback_data='back_odrers')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


def keyboard_count_people() -> None:
    """
    Клавиатура для вовращения после редактирования
    :return:
    """
    button_1 = InlineKeyboardButton(text='Продолжить',
                                    callback_data='pass_people')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]],
    )
    return keyboard


def keyboard_finish_orders() -> None:
    """
    Клавиатура для вовращения после редактирования
    :return:
    """
    button_1 = InlineKeyboardButton(text='Отправить',
                                    callback_data='send_orders')
    button_2 = InlineKeyboardButton(text='Отмена',
                                    callback_data='cancel_orders')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard

def keyboard_finish_orders_one_press() -> None:
    """
    Клавиатура для вовращения после редактирования
    :return:
    """
    button_1 = InlineKeyboardButton(text='Отпрaвить',
                                    callback_data=' ')
    button_2 = InlineKeyboardButton(text='Отмeна',
                                    callback_data=' ')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard

# клавиатура подтверждения готовности участия в заказе с id = id_services
def keyboard_ready_player(id_order) -> None:

    button_1 = InlineKeyboardButton(text='Да',
                                    callback_data=f'ready_yes_{id_order}')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]],
    )
    return keyboard


def keyboard_send_report(id_order) -> None:
    """
    Клавиатура для вовращения после редактирования
    :return:
    """
    button_1 = InlineKeyboardButton(text='ОТЧЕТ',
                                    callback_data=f'report_{id_order}')
    button_2 = InlineKeyboardButton(text='Заменить',
                                    callback_data=f'change_player_{id_order}')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1], [button_2]],
    )
    return keyboard


def keyboard_append_channel_and_group() -> None:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Канал',
                                    callback_data='add_channel')
    button_2 = InlineKeyboardButton(text='Беседа',
                                    callback_data='add_group')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


def keyboard_change_player(id_order) -> None:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Заменить',
                                    callback_data=f'change_player_{id_order}')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]],
    )
    return keyboard


def keyboard_confirm_report() -> None:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Да',
                                    callback_data='yesreport')
    button_2 = InlineKeyboardButton(text='Нет',
                                    callback_data='noreport')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard


def keyboard_confirm_change(id_order) -> None:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Да',
                                    callback_data=f'yeschange_{id_order}')
    button_2 = InlineKeyboardButton(text='Нет',
                                    callback_data='nochange')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard