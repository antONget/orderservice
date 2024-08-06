from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging


def keyboard_append_channel_and_group() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора ресурса
    :return:
    """
    logging.info('keyboard_append_channel_and_group')
    button_1 = InlineKeyboardButton(text='Канал',
                                    callback_data='add_channel')
    button_2 = InlineKeyboardButton(text='Беседа',
                                    callback_data='add_group')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard
