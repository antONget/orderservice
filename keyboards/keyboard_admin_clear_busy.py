from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# УСЛУГА
def keyboard_busy() -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения очистки занятости
    :return:
    """
    button_1 = InlineKeyboardButton(text='Очистить',
                                    callback_data='clear_busy')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard
