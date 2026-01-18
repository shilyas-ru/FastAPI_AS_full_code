# Основной файл для работы с подключением к базе данных.
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

# Подключение к базе данных
# engine = create_async_engine(settings.DB_URL)
engine = create_async_engine(settings.DB_URL)
# engine = create_async_engine(settings.DB_URL, echo=True)
# Строка генерирует такой SQL-запрос (способ хорош для базового понимания):
# BEGIN (implicit)
# INSERT INTO hotels (title, location) VALUES ($1::VARCHAR, $2::VARCHAR) RETURNING hotels.id
# [generated in 0.00018s] ('title Сочи', 'location Сочи')
# COMMIT

# print(f"Строка для подключения:\n{settings.DB_URL=}")

# Создаём объект сессии
# Параметр expire_on_commit будет описан позже
# async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    # Этот класс нужен, чтобы от него наследовались все модели в проекте.
    pass
