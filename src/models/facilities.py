from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped

from src.database import Base


class FacilitiesORM(Base):
    # Справочник удобств

    # Наименование таблицы
    __tablename__ = "facilities"

    # Столбцы

    # Первичный ключ, уникальное значение
    id: Mapped[int] = mapped_column(primary_key=True)

    # Наименование удобства
    # length= можно не указывать, тогда будет так:
    # title: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(length=100))


class RoomsFacilitiesORM(Base):
    # Отвечает за связь many-to-many

    # Наименование таблицы - отображаем, что связываем две таблицы: rooms и facilities.
    __tablename__ = "rooms_facilities"

    # Столбцы

    # Первичный ключ, уникальное значение
    id: Mapped[int] = mapped_column(primary_key=True)

    # Внешний ключ привязывающий к номеру
    # Идентификатор номера, в котором находится удобство
    # ForeignKey("название_таблицы.название_столбца")
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))

    # Внешний ключ привязывающий к удобствам
    # Идентификатор удобства, которое находится в номере
    # ForeignKey("название_таблицы.название_столбца")
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))


