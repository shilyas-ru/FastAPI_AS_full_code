# Основной файл для работы с подключением к базе данных.
import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase

from src.config import settings


engine = create_async_engine(settings.DB_URL)
# print(f"Строка для подключения:\n{settings.DB_URL=}")

# # Пример работы с сырым (чистым) запросом SQL
# async def raw_sql_query():
#     async with engine.begin() as conn:
#         res = await conn.execute(text("SELECT version()"))
#         print(res.fetchone())  # Возврат одной строки
#
# asyncio.run(raw_sql_query())


class Base(DeclarativeBase):
    # Этот класс нужен, чтобы от него наследовались все модели в проекте.
    pass

# Создаём объект сессии
# Параметр expire_on_commit будет описан позже
# async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
#
# session = async_session_maker()
# await session.execute()  # Тут описываем, какой код надо исполнить - не обязательно
                           # сырые SQL запросы, но конструкции из SQLAlchemy.