from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboards_main_user():
    button_2 = KeyboardButton(text='Баланс')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_2]],
                                   resize_keyboard=True)
    return keyboard
