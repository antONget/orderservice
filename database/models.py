from sqlalchemy import BigInteger, String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url="sqlite+aiosqlite:///database/db.sqlite3", echo=False)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    token_auth: Mapped[str] = mapped_column(String(20))
    telegram_id = mapped_column(BigInteger, default=0)
    username: Mapped[str] = mapped_column(String(20), default='username')
    is_admin: Mapped[int] = mapped_column(Integer, default=0)
    is_busy: Mapped[int] = mapped_column(Float, default=0)


class Statistic(Base):
    __tablename__ = 'statistics'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer)
    cost_order: Mapped[int] = mapped_column(Integer)
    order_id: Mapped[int] = mapped_column(Integer)



class Service(Base):
    __tablename__ = 'services'

    id: Mapped[int] = mapped_column(primary_key=True)
    title_services: Mapped[str] = mapped_column(String(20))
    cost_services: Mapped[int] = mapped_column(Integer)
    count_services: Mapped[int] = mapped_column(Integer)
    picture_services: Mapped[str] = mapped_column(String(200), default='None')


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(Integer)
    title_services: Mapped[str] = mapped_column(String(20))
    cost_services: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(String(200))
    count_people: Mapped[int] = mapped_column(Integer)
    report: Mapped[str] = mapped_column(String(200), default='report')


class Executor(Base):
    __tablename__ = 'executor'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer)
    id_order: Mapped[int] = mapped_column(Integer)
    cost_order: Mapped[int] = mapped_column(Integer)
    status_executor: Mapped[str] = mapped_column(String(20))
    message_id: Mapped[int] = mapped_column(Integer)
    change_id: Mapped[int] = mapped_column(Integer, default=0)


class Channel(Base):
    __tablename__ = 'channels'

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(200))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
