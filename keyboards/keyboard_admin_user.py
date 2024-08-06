from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


# ПОЛЬЗОВАТЕЛЬ - [Добавить][Удалить]
def keyboard_edit_list_user() -> InlineKeyboardMarkup:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Добавить',
                                    callback_data='add_user')
    button_2 = InlineKeyboardButton(text='Удалить',
                                    callback_data='delete_user')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard


# ПОЛЬЗОВАТЕЛЬ -> Удалить
def keyboards_del_users(list_users, back, forward, count):
    """
    Клавиатура для выбора пользователя для удаления
    :param list_users:
    :param back:
    :param forward:
    :param count:
    :return:
    """
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_users)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток, то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for user in list_users[back*count:(forward-1)*count]:
        text = user.username
        button = f'deleteuser_{user.telegram_id}'
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
    return kb_builder.as_markup()


# ПОЛЬЗОВАТЕЛЬ -> Удалить -> подтверждение удаления пользователя из базы
def keyboard_delete_user() -> InlineKeyboardMarkup:
    """
    Клавиатура для редактирования списка администраторов
    :return:
    """
    button_1 = InlineKeyboardButton(text='Удалить',
                                    callback_data='del_user')
    button_2 = InlineKeyboardButton(text='Отмена',
                                    callback_data='notdel_user')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard
