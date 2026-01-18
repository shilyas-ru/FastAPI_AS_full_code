from datetime import date

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from src.database import Base


class BookingsORM(Base):
    # Наименование таблицы
    __tablename__ = "bookings"

    # Первичный ключ, уникальное значение
    id: Mapped[int] = mapped_column(primary_key=True)

    # Внешний ключ привязывающий к номеру
    # Идентификатор забронированного номера
    # ForeignKey("название_таблицы.название_столбца")
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))

    # Внешний ключ привязывающий к пользователю
    # Идентификатор пользователя, забронировавшего номер
    # ForeignKey("название_таблицы.название_столбца")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Дата, С которой бронируется номер.
    # Если не указываем параметры поля, то mapped_column() можно опустить.
    # Делаем допущение, что цена всегда круглая, нет никаких копеек
    date_from: Mapped[date]

    # Дата, ДО которой бронируется номер.
    # Если не указываем параметры поля, то mapped_column() можно опустить.
    # Делаем допущение, что цена всегда круглая, нет никаких копеек
    date_to: Mapped[date]

    # Цена, по которой забронирован номер.
    # Если не указываем параметры поля, то mapped_column() можно опустить.
    # Делаем допущение, что цена всегда круглая, нет никаких копеек
    price: Mapped[int]

    @hybrid_property
    def total_cost(self) -> int:
        # (self.date_to - self.date_from) - это объект timedelta. Берём дни (days).
        return self.price * (self.date_to - self.date_from).days


