from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, INT
from src.database import Base


class UsersORM(Base):
    # Наименование таблицы
    __tablename__ = "users"

    # Столбцы

    # Первичный ключ, уникальное значение
    id: Mapped[int] = mapped_column(primary_key=True)

    # Электронная почта пользователя
    email: Mapped[str] = mapped_column(String(length=200), unique=True)

    # Хэшированный пароль.
    hashed_password: Mapped[str] = mapped_column(String(length=200))

    # # Ниже строки не внесены в БД, потом обработать надо.
    # # Это гипотетические параметры о пользователе.
    # # Ник
    # nick_name: str | None = None
    #
    # # Полное имя
    # full_name: str | None = None
    #
    # # Заблокирован пользователь или нет
    # disabled: bool | None = None



