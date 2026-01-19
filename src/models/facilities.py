from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped, relationship

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

    # Связь relationship с таблицей
    # В атрибуте rooms будут все номера, в которых имеется это удобство

    # "RoomsORM" импортировать не надо, так как это является
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

    # back_populates="facilities" - аргумент "facilities" это наименование
    # атрибута relationship, указанного в другом классе (в классе RoomsORM)

    rooms: Mapped[list["RoomsORM"]] = relationship(
        back_populates="facilities",
        secondary="rooms_facilities"
    )


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


