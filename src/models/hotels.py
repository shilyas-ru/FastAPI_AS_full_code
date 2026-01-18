from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, INT
from src.database import Base


class HotelsORM(Base):
    # Наименование таблицы
    __tablename__ = "hotels"

    # Столбцы

    # Первичный ключ, уникальное значение
    id: Mapped[int] = mapped_column(primary_key=True)

    # Наименование отеля
    title: Mapped[str] = mapped_column(String(length=100))

    # Местонахождение отеля.
    location: Mapped[str]


