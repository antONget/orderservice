from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon import lexicon_ru
import logging

def keyboards_superadmin():
    button_1 = KeyboardButton(text='Администраторы')
    button_2 = KeyboardButton(text='Услуга')
    button_3 = KeyboardButton(text='Пользователь')
    button_4 = KeyboardButton(text='Канал')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2, button_3, button_4]],
        resize_keyboard=True
    )
    return keyboard


def keyboards_admin():
    button_2 = KeyboardButton(text='Услуга')
    button_3 = KeyboardButton(text='Пользователь')
    button_4 = KeyboardButton(text='Канал')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_2, button_3, button_4]],
        resize_keyboard=True
    )
    return keyboard


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


def keyboard_edit_list_services() -> None:
    """
    Клавиатура для редактирования списка администраторов
    :return:
    """
    button_1 = InlineKeyboardButton(text='Добавить',
                                    callback_data='add_services')
    button_2 = InlineKeyboardButton(text='Изменить',
                                    callback_data='delete_services')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


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
