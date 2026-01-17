from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, INT
from src.database import Base


class HotelsORM(Base):
    # Наименование таблицы
    __tablename__ = "hotels"

    # Столбцы

    # Если планируется большая БД, то надо смотреть на кол-во значений,
    # допускаемых типом данных. Возможно, потребуется большое число.
    # Про типы можно посмотреть тут: https://postgrespro.ru/docs/postgrespro/15/datatype-numeric
    # smallint	2 байта	целое в небольшом диапазоне	-32768 .. +32767
    # integer	4 байта	типичный выбор для целых чисел	-2147483648 .. +2147483647
    # bigint	8 байт	целое в большом диапазоне	-9223372036854775808 .. 9223372036854775807
    # или тут: "The Type Hierarchy", https://docs.sqlalchemy.org/en/20/core/type_basics.html

    # Первичный ключ, уникальное значение
    id: Mapped[int] = mapped_column(primary_key=True)

    # Наименование отеля
    # length= можно не указывать, тогда будет так:
    # title: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(length=100))

    # Местонахождение отеля.
    # Если не указываем параметры поля, то mapped_column() можно опустить.
    location: Mapped[str]


