from database.models import User, Order, Statistic, Channel, Service
from database.models import async_session
from sqlalchemy import select, update, delete
from dataclasses import dataclass
import logging


@dataclass
class UserRole:
    user = 0
    admin = 1


async def add_super_admin(data: dict):
    """
    Добавление в базу супер-админа
    :param data:
    :return:
    """
    logging.info(f'add_super_admin')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == data["telegram_id"]))
        if not user:
            session.add(User(**data))
            await session.commit()


async def add_token(data: dict):
    """
    Добавление в базу супер-админа
    :param data:
    :return:
    """
    logging.info(f'add_super_admin')
    async with async_session() as session:
        session.add(User(**data))
        await session.commit()


async def add_user(telegram_id: int, username: str, token: str):
    """
    Добавление пользователя в БД по token
    :param telegram_id:
    :param username:
    :param token:
    :return:
    """
    logging.info(f'set_username_admin')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.token_auth == token))
        user.username = username
        user.telegram_id = telegram_id
        await session.commit()


async def get_all_users():
    """
    Получаем список всех пользователей зарегистрированных в боте
    :return:
    """
    logging.info(f'get_all_users')
    async with async_session() as session:
        users = await session.scalars(select(User).where(User.telegram_id != 0))
        return users


async def get_user_tg_id(tg_id: int):
    """
    Получаем информацию по пользователю
    :param tg_id:
    :return:
    """
    logging.info(f'get_user_tg_id')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tg_id))
        return user


async def get_list_admins(is_admin: 0):
    """
    Получаем список администраторов/не администраторов
    :param is_admin:
    :return:
    """
    logging.info(f'get_list_admins')
    async with async_session() as session:
        list_admins = await session.scalars(select(User).where(User.is_admin == is_admin, User.telegram_id != 0))
        return list_admins


async def set_username_admin(telegram_id: int, username: str):
    """
    Обновление имени администратора
    :param telegram_id:
    :param username:
    :return:
    """
    logging.info(f'set_username_admin')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        user.username = username
        await session.commit()


async def set_role_user(telegram_id: int, is_admin: int):
    """
    Обновление роли пользователя
    :param telegram_id:
    :param is_admin:
    :return:
    """
    logging.info(f'set_username_admin')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        user.is_admin = is_admin
        await session.commit()


async def set_busy_id(telegram_id: int, busy: int):
    """
    Обновление роли пользователя
    :param telegram_id:
    :param busy:
    :return:
    """
    logging.info(f'set_username_admin')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        user.is_busy = busy
        await session.commit()


async def clear_stat():
    """
    Обнуление статистики
    :return:
    """
    logging.info(f'clear_stat')
    async with async_session() as session:
        users = await session.scalars(select(User))
        for user in users:
            user.is_busy = 0
        await session.commit()


async def check_token(token: str):
    """
    Валидация токена
    :param token:
    :return:
    """
    logging.info(f'check_token')
    async with async_session() as session:
        return await session.scalar(select(User).where(User.token_auth == token))


async def delete_user(tg_id: int):
    """
    Удаление пользователя
    :param tg_id: id телеграм пользователя
    :return:
    """
    logging.info(f'delete_user')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tg_id))
        await session.delete(user)
        await session.commit()


async def select_all_data_statistic():
    """
    Получаем записи из таблицы "Статистика"
    :return:
    """
    logging.info('select_alldata_statistic')
    async with async_session() as session:
        return await session.scalars(select(Statistic))


async def check_statistic():
    """
    Удаляем таблицу со статистикой
    :return:
    """
    logging.info('delete_statistic')
    async with async_session() as session:
        return await session.scalar(select(Statistic))


async def delete_statistic():
    """
    Удаляем таблицу со статистикой
    :return:
    """
    logging.info('delete_statistic')
    async with async_session() as session:
        statistics = await session.scalar(select(Statistic))
        await session.delete(statistics)
        await session.commit()


async def add_resource(data: dict):
    """
    Обновление канала/группы
    :param data:
    :return:
    """
    logging.info(f'set_username_admin')
    async with async_session() as session:
        channel = await session.scalar(select(Channel).where(Channel.channel_id == data["channel_id"]))
        if not channel:
            session.add(Channel(**data))
        await session.commit()


async def add_service(data: dict):
    """
    Добавление новой услуги
    :param data:
    :return:
    """
    logging.info(f'add_service')
    async with async_session() as session:
        session.add(Service(**data))
        await session.commit()


async def get_service():
    """
    Получаем услуги
    :return:
    """
    logging.info(f'add_service')
    async with async_session() as session:
        return await session.scalars(select(Service))


async def get_service_id(service_id: int) -> Service:
    """
    Выбор услуги по id
    :param service_id:
    :return:
    """
    logging.info(f'delete_user')
    async with async_session() as session:
        return await session.scalar(select(Service).where(Service.id == service_id))


async def delete_service(service_id: int):
    """
    Удаляем таблицу со статистикой
    :param service_id:
    :return:
    """
    logging.info('delete_service')
    async with async_session() as session:
        service = await session.scalar(select(Service).where(Service.id == service_id))
        await session.delete(service)
        await session.commit()


async def update_service_id(service_id: int, title_service: str, cost_service: int):
    """
    Обновление роли пользователя
    :param service_id:
    :param title_service:
    :param cost_service:
    :return:
    """
    logging.info(f'set_username_admin')
    async with async_session() as session:
        service = await session.scalar(select(Service).where(Service.id == service_id))
        service.title_services = title_service
        service.cost_services = cost_service
        await session.commit()


async def add_order(data: dict):
    """
    Добавление в базу заказа
    :param data:
    :return:
    """
    logging.info(f'add_order')
    async with async_session() as session:
        session.add(Order(**data))
        await session.commit()


async def get_orders() -> list:
    """
    Получаем заказы
    :return:
    """
    logging.info(f'get_orders')
    async with async_session() as session:
        return await session.scalars(select(Order))


async def update_list_sandler(list_mailing_str: str, id_order: int):
    """
    Обновляем список рассылки для заказа
    :param list_mailing_str:
    :param id_order:
    :return:
    """
    logging.info(f'update_list_sendlers')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == id_order))
        order.sandler = list_mailing_str
        await session.commit()


async def get_orders_id(order_id: int) -> Order:
    """
    Получаем заказ по его id
    :return:
    """
    logging.info(f'get_orders_id')
    async with async_session() as session:
        return await session.scalars(select(Order).where(Order.id == order_id))


async def delete_order(order_id: int):
    """
    Удаление заказа по id
    :param order_id:
    :return:
    """
    logging.info(f'delete_user')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        await session.delete(order)
        await session.commit()
