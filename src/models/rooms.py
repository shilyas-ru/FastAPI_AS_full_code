from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from src.database import Base


class RoomsORM(Base):
    # Наименование таблицы
    __tablename__ = "rooms"

    # Столбцы
    # Из статьи "Асинхронный SQLAlchemy 2: простой пошаговый гайд по
    # настройке, моделям, связям и миграциям с использованием Alembic"
    # https://habr.com/ru/companies/amvera/articles/849836/
    #
    # Mapped — это современный способ аннотировать типы данных
    # для колонок в моделях SQLAlchemy. Он позволяет более четко
    # указать, что переменная представляет собой колонку таблицы
    # в базе данных, делая код более читаемым и понятным.

    # Первичный ключ, уникальное значение
    id: Mapped[int] = mapped_column(primary_key=True)

    # Внешний ключ привязывающий к отелю
    # Идентификатор отеля, в котором находится комната
    # ForeignKey("название_таблицы.название_столбца")
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))

    # Наименование номера
    # length= можно не указывать, тогда будет так:
    # title: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(length=100))

    # Описание номера. Параметр факультативный (может отсутствовать).
    # Если не указываем параметры поля, то mapped_column() можно опустить.
    description: Mapped[str | None]

    # Цена номера.
    # Если не указываем параметры поля, то mapped_column() можно опустить.
    # Делаем допущение, что цена всегда круглая, нет никаких копеек
    price: Mapped[int]

    # Общее количество номеров такого типа (например,
    # однокомнатных - 20 шт., двухкомнатных - 15 шт.).
    # Если не указываем параметры поля, то mapped_column() можно опустить.
    quantity: Mapped[int]

    # Связь relationship с таблицей
    # В атрибуте facilities будут все удобства, имеющиеся в этом номере

    # "FacilitiesOrm" импортировать не надо, так как это является
    # строкой (пишем в кавычках), а ссылкой на соответствующий класс.

    # Параметр secondary - через какую таблицу связываем номера и удобства.
    # Это таблица M2M, в нашем случае - она описывается в классе
    # RoomsFacilitiesORM(Base) в файле src\models\facilities.py.

    # Параметр back_populates обеспечивает двунаправленную навигацию,
    # обеспечивая доступ к связанному объекту User из объекта Profile
    # и от объекта RoomsORM к объекту FacilitiesORM. Поскольку в этом примере
    # мы используем back_populates в отличие от backref, необходимо определить
    # отношение с обеих сторон, в то время как с backref нам нужно будет
    # определить отношение только с одной стороны (только в рамках одной модели).

    # back_populates="rooms" - аргумент "rooms" - это наименование атрибута
    # relationship, указанного в другом классе (в классе RoomsORM)

    facilities: Mapped[list["FacilitiesORM"]] = relationship(
        back_populates="rooms",
        secondary="rooms_facilities"
    )



