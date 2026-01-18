from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, INT
from src.database import Base


class UsersORM(Base):
    # Наименование таблицы
    __tablename__ = "users"

    # Столбцы

    # Первичный ключ, уникальное значение
    id: Mapped[int] = mapped_column(primary_key=True)

    # Наименование отеля
    email: Mapped[str] = mapped_column(String(length=200), unique=True)

    # Местонахождение отеля.
    hashed_password: Mapped[str] = mapped_column(String(length=200))



