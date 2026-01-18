from datetime import date

from pydantic import BaseModel, Field, ConfigDict

bookings_info = {"room_id": "Идентификатор забронированного номера",
                 "user_id": "Идентификатор пользователя, забронировавшего номер",
                 "date_from": "Дата, С которой бронируется номер",
                 "date_to": "Дата, ДО которой бронируется номер",
                 "price": "Цена номера",
                 }

bookings_examples = {"room_id": 1,  # int, Идентификатор забронированного номера
                     "user_id": 1,  # int, Идентификатор пользователя, забронировавшего номер
                     # "date_from": date.today(),  # date: 2025-01-23, Дата, С которой бронируется номер
                     "date_from": "2025-01-22",  # date: 2025-01-23, Дата, С которой бронируется номер
                     # "date_to": date.today(),  # date: 2025-01-23, Дата, ДО которой бронируется номер
                     "date_to": "2025-01-27",  # date: 2025-01-23, Дата, ДО которой бронируется номер
                     "price": 111,  # int, Цена номера
                     }


class BookingsHotelPath(BaseModel):
    # Поля указываем такие же, как в дальнейшем будем указывать в ссылках:
    # @router.delete("/{hotel_id}",...
    # Если поле в классе и имя переменной в ссылке будут различными, то возникнет
    # ошибка "422 unprocessable entity"
    hotel_id: int = Field(description="Идентификатор отеля",
                          ge=1,
                          examples=[1],
                          )


class BookingsRoomPath(BaseModel):
    # Поля указываем такие же, как в дальнейшем будем указывать в ссылках:
    # @router.delete("/{hotel_id}",...
    # Если поле в классе и имя переменной в ссылке будут различными, то возникнет
    # ошибка "422 unprocessable entity"
    room_id: int = Field(description="Идентификатор комнаты",
                         ge=1,
                         examples=[1],
                         )


class BookingsHotelRoomPath(BookingsRoomPath, BookingsHotelPath):
    pass


class BookingsInfoRecRequest(BaseModel):
    # Данные передаются из запроса
    # Поля указываем такие же, как именованы колонки в таблице
    # bookings (класс BookingsORM в файле src\models\bookings.py).
    date_from: date = Field(description=bookings_info["date_from"],
                            examples=[bookings_examples["date_from"]],
                            )
    date_to: date = Field(description=bookings_info["date_to"],
                          examples=[bookings_examples["date_to"]],
                          )


class BookingsInfoRecURL(BookingsInfoRecRequest):
    # Данные из запроса дополняются информацией из URL
    # Поля указываем такие же, как именованы колонки в таблице
    # bookings (класс BookingsORM в файле src\models\bookings.py).
    room_id: int = Field(description=bookings_info["room_id"],
                         ge=1,
                         examples=[bookings_examples["room_id"]],
                         )


class BookingsInfoRecFull(BookingsInfoRecURL):
    # Данные, дополненные из URL, дополняются вычисляемыми данными:
    # идентификатор пользователя и цена номера.
    user_id: int = Field(description=bookings_info["user_id"],
                         ge=1,
                         examples=[bookings_examples["user_id"]],
                         )
    price: int = Field(description=bookings_info["price"],
                       ge=1,
                       examples=[bookings_examples["price"]],
                       )


# Класс определяет даты для поиска отелей/номеров, свободных в эти даты от брони
class BookingDateParams(BaseModel):
    date_from: date | None = Field(default=None,
                                   example='2025-01-20',
                                   description="Дата, С которой бронируется номер",
                                   )
    date_to: date | None = Field(default=None,
                                 example='2025-01-23',
                                 description="Дата, ДО которой бронируется номер",
                                 )


# Класс определяет пагинацию, включающую вывод по страницам или вывод всего списка сразу
class BookingHotelsParams(BookingDateParams):
    hotels_with_free_rooms: bool | None = Field(default=None,
                                                alias="hotels-with-free-rooms",
                                                description="Отели со свободными номерами "
                                                            "в указанные даты "
                                                            "(True) или полный список отелей "
                                                            "не учитывая указанные даты"
                                                            "(False или None)",
                                                )


# Класс определяет пагинацию, включающую вывод по страницам или вывод всего списка сразу
class BookingRoomsParams(BookingDateParams):
    free_rooms: bool | None = Field(default=None,
                                    alias="free-rooms",
                                    description="Выбирать свободные (не забронированные) "
                                                "номера в указанные даты (True) "
                                                "или выбирать полный список номеров, "
                                                "не учитывая указанные даты"
                                                "(False или None)",
                                    )


# Сделано по аналогии с другими схемами: BookingsBase и BookingsPydanticSchema.
# BookingsPydanticSchema используется в BookingsRepository.
class BookingsBase(BaseModel):
    # Поля указываем такие же, как именованы колонки в таблице
    # bookings (класс BookingORM в файле src\models\bookings.py).
    room_id: int = Field()
    user_id: int = Field()
    date_from: date | None = Field(default=None)
    date_to: date | None = Field(default=None)
    price: int | None = Field(default=None)


class BookingsPydanticSchema(BookingsBase):
    # Эта схема должна иметь такие же поля, как указаны в схеме
    # для отелей - hotels (класс HotelsORM в файле src\models\hotels.py).
    # Поля title и location наследуем от родителя.
    id: int = Field()

    model_config = ConfigDict(from_attributes=True)
