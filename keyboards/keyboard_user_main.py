from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboards_main_user() -> ReplyKeyboardMarkup:
    button_1 = KeyboardButton(text='Баланс')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]],
                                   resize_keyboard=True)
    return keyboard


def keyboard_change_player(id_order: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для замены в заказе
    :return:
    """
    button_1 = InlineKeyboardButton(text='Заменить',
                                    callback_data=f'change_player_{id_order}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard


def keyboard_send_report(id_order: int) -> InlineKeyboardMarkup:
    """
    Клавиатура добавляет отчет к кнопке ЗАМЕНИТЬ
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


def keyboard_confirm_change(id_order: int) -> InlineKeyboardMarkup:
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


def keyboard_ready_player_() -> None:

    button_1 = InlineKeyboardButton(text='Подождите...',
                                    callback_data='---')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]],
    )
    return keyboard


def keyboard_ready_player(id_order) -> InlineKeyboardMarkup:
    """
    Устанавливаем клавиатуру для пользователей после окончания рассылки
    :param id_order:
    :return:
    """
    button_1 = InlineKeyboardButton(text='Да',
                                    callback_data=f'ready_yes_{id_order}')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard


def keyboard_confirm_report() -> InlineKeyboardMarkup:
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
