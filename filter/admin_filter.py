from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from config_data.config import load_config, Config
import database.requests as rq
import logging

config: Config = load_config()


async def check_super_admin(telegram_id: int) -> bool:
    """
    Проверка на администратора
    :param telegram_id: id пользователя телеграм
    :return: true если пользователь администратор, false в противном случае
    """
    logging.info('check_super_admin')
    list_super_admin = config.tg_bot.admin_ids.split(',')
    return str(telegram_id) in list_super_admin


async def check_user_role(tg_id: int, user_role: int = 1) -> bool:
    """
    Проверка, что пользователь администратор
    :param tg_id:
    :param user_role:
    :return:
    """
    logging.info(f'check_personal')
    info_user = await rq.get_user_tg_id(tg_id=tg_id)
    if info_user:
        return info_user.is_admin == user_role
    else:
        return False


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        info_user = await rq.get_user_tg_id(tg_id=message.chat.id)
        if info_user:
            return info_user.is_admin == rq.UserRole.admin
        else:
            return False


class IsUserM(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        info_user = await rq.get_user_tg_id(tg_id=message.chat.id)
        if info_user:
            return info_user.is_admin == rq.UserRole.admin or info_user.is_admin == rq.UserRole.user
        else:
            return False


class IsUserC(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        info_user = await rq.get_user_tg_id(tg_id=callback.message.chat.id)
        if info_user:
            return info_user.is_admin == rq.UserRole.admin or info_user.is_admin == rq.UserRole.user
        else:
            return False


class IsSuperAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return await check_super_admin(telegram_id=message.chat.id)


async def check_personal(tg_id: int, role: str = 'personal') -> bool:
    """
    Проверка роли пользователя
    :param tg_id:
    :param role:
    :return:
    """
    logging.info(f'check_personal')
    info_user = await rq.get_user_tg_id(tg_id=tg_id)
    if role == "personal":
        if info_user.role not in [rq.UserRole.user]:
            return True
        else:
            return False
    else:
        if info_user.role == role or info_user.role == rq.UserRole.admin:
            return True
        else:
            return False

