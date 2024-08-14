from database.models import User, Order, Statistic, Channel, Service, Executor
from database.models import async_session
from sqlalchemy import select, update, delete
from dataclasses import dataclass
import logging


"""USER"""


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
        user = await session.scalar(select(User).where(User.telegram_id == int(data["telegram_id"])))
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


async def get_all_users() -> User:
    """
    Получаем список всех пользователей зарегистрированных в боте
    :return:
    """
    logging.info(f'get_all_users')
    async with async_session() as session:
        users = await session.scalars(select(User).where(User.telegram_id != 0))
        return users


async def get_all_users_not_admin():
    """
    Получаем список всех пользователей зарегистрированных в боте
    :return:
    """
    logging.info(f'get_all_users')
    async with async_session() as session:
        users = await session.scalars(select(User).where(User.telegram_id != 0, User.is_admin == 0))
        return users


async def get_user_tg_id(tg_id: int) -> User:
    """
    Получаем информацию по пользователю
    :param tg_id:
    :return:
    """
    logging.info(f'get_user_tg_id')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tg_id))
        return user


async def get_list_admins(is_admin: int) -> User:
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
        return await session.scalar(select(User).where(User.token_auth == token, User.telegram_id == 0))


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


"""STATISTIC"""


async def add_statistic(data: dict):
    """
    Добавление статистики
    :param data:
    :return:
    """
    logging.info(f'add_static')
    async with async_session() as session:
        session.add(Statistic(**data))
        await session.commit()


async def select_all_data_statistic():
    """
    Получаем записи из таблицы "Статистика"
    :return:
    """
    logging.info('select_alldata_statistic')
    async with async_session() as session:
        return await session.scalars(select(Statistic))


async def get_statistic_tg_id(tg_id: int) -> Statistic:
    """
    Получаем записи из таблицы "Статистика" для пользователя по его id
    :param tg_id:
    :return:
    """
    logging.info('select_alldata_statistic')
    async with async_session() as session:
        return await session.scalars(select(Statistic).where(Statistic.tg_id == tg_id))


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
        statistics = await session.scalars(select(Statistic))
        for statistic in statistics:
            await session.delete(statistic)
        await session.commit()


"""CHANNEL"""


async def add_resource(data: dict):
    """
    Добавление канала/группы
    :param data:
    :return:
    """
    logging.info(f'add_resource')
    async with async_session() as session:
        channel = await session.scalar(select(Channel).where(Channel.channel_id == data["channel_id"]))
        if not channel:
            session.add(Channel(**data))
            await session.commit()


async def get_channels() -> Channel:
    """
    Получаем ресурсы для публикации
    :return:
    """
    logging.info(f'get_channels')
    async with async_session() as session:
        return await session.scalars(select(Channel))


"""SERVICE"""


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


"""ORDER"""


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


async def get_orders() -> Order:
    """
    Получаем заказы
    :return:
    """
    logging.info(f'get_orders')
    async with async_session() as session:
        return await session.scalars(select(Order))


async def get_order_id(order_id: int) -> Order:
    """
    Получаем заказ по его id
    :param order_id:
    :return:
    """
    logging.info(f'get_orders_id')
    async with async_session() as session:
        return await session.scalar(select(Order).where(Order.id == order_id))


async def set_order_report(order_id: int, report: str) -> None:
    """
    Обновляем отчет заказа
    :param order_id:
    :param report:
    :return:
    """
    logging.info(f'set_order_report')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        if order:
            order.report = report
            await session.commit()


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


"""EXECUTOR"""


@dataclass
class ExecutorStatus:
    none = "none"
    done = "done"
    change = "change"
    cancel = "cancel"
    complete = "complete"


async def add_executor(data: dict) -> None:
    """
    Добавление потенциального исполнителя заказа в БД
    :param data:
    :return:
    """
    logging.info(f'add_order')
    async with async_session() as session:
        session.add(Executor(**data))
        await session.commit()


async def get_executors_order_id(order_id: int) -> Executor:
    """
    Получаем список исполнителей кому был разослан заказ {order_id}
    :param order_id:
    :return:
    """
    logging.info(f'get_executors_order_id')
    async with async_session() as session:
        return await session.scalars(select(Executor).where(Executor.id_order == order_id))


async def get_executor_tg_id_order_id(order_id: int, tg_id: int) -> Executor:
    """
    Получаем информацию по исполнителю заказа {order_id} по его id телеграм {tg_id}
    :param order_id:
    :param tg_id:
    :return:
    """
    logging.info(f'get_executors_order_id')
    async with async_session() as session:
        return await session.scalar(select(Executor).where(Executor.id_order == order_id, Executor.tg_id == tg_id))


async def get_executors_status_order_id(order_id: int, status: str) -> Executor:
    """
    Получаем информацию по исполнителям заказа {order_id} по их статусу
    :param order_id:
    :param status:
    :return:
    """
    logging.info(f'get_executors_order_id')
    async with async_session() as session:
        return await session.scalars(select(Executor).where(Executor.id_order == order_id,
                                                            Executor.status_executor == status))


async def set_executors_status_tg_id_order_id(order_id: int, tg_id: int, status: str) -> None:
    """
    Обновляем статус заказа {order_id} на {status} у пользователя по его id телеграм {tg_id}
    :param order_id:
    :param tg_id:
    :param status:
    :return:
    """
    logging.info(f'get_executors_order_id {order_id} {tg_id} {status}')
    async with async_session() as session:
        executor = await session.scalar(select(Executor).where(Executor.id_order == order_id, Executor.tg_id == tg_id))
        if executor:
            executor.status_executor = status
            await session.commit()


async def get_executor_tg_id_status(tg_id: int, status: str) -> Executor:
    """
    Получаем заказ пользователя по его id телеграм {tg_id} с заданным статусом заказа {status}
    :param tg_id:
    :param status:
    :return:
    """
    logging.info(f'get_orders_id')
    async with async_session() as session:
        return await session.scalar(select(Executor).where(Executor.tg_id == tg_id, Executor.status_executor == status))


async def set_executors_change_tg_id_order_id(order_id: int, tg_id: int, change_id: int) -> None:
    """
    Обновляем замену в заказе {order_id} у пользователя по его id телеграм {change_id}
    :param order_id:
    :param tg_id:
    :param change_id:
    :return:
    """
    logging.info(f'get_executors_order_id {order_id} {tg_id}')
    async with async_session() as session:
        executor = await session.scalar(select(Executor).where(Executor.id_order == order_id, Executor.tg_id == tg_id))
        if executor:
            executor.change_id = change_id
            await session.commit()


async def delete_executor(tg_id: int, order_id: int):
    """
    Удаление исполнителя по id
    :param tg_id:
    :param order_id:
    :return:
    """
    logging.info(f'delete_executor')
    async with async_session() as session:
        executor = await session.scalar(select(Executor).where(Executor.tg_id == tg_id, Executor.id_order == order_id))
        if executor:
            await session.delete(executor)
            await session.commit()
