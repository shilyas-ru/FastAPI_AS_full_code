from datetime import date

from fastapi import Body, Path, APIRouter, Query
from typing import Annotated

from sqlalchemy import select as sa_select  # Для реализации SQL команды SELECT
from sqlalchemy import delete as sa_delete  # Для реализации SQL команды DELETE

from src.api.dependencies.dependencies import DBDep, PaginationAllDep, PaginationPagesDep
from src.schemas.facilities import RoomsFacilityBase

from src.schemas.rooms import RoomPath, HotelRoomPath, HotelPath, RoomPydanticSchema, RoomBase, RoomWithRels
from src.schemas.rooms import RoomDescriptionRecURL, RoomDescrRecRequest
from src.schemas.rooms import RoomDescriptionOptURL, RoomDescrOptRequest


"""
- Полное именование URL:
    - /hotels/{hotel_id}/rooms/{rooms_id}
    Используется, если требуется указать идентификатор отеля и идентификатор номера.
    - /hotels/rooms/{rooms_id}
    Используется, если требуется указать идентификатор номера, а идентификатор отеля 
    в адресе не указывается.
    Такой вариант может использоваться, если идентификатор отеля передаётся в другом 
    запросе, например, через тело запроса.

- Необходимо реализовать для номеров:
    1. Вывести информацию по всем номерам отеля
    2. Выбрать инфо по конкретному номеру по id
    3. Добавить номер с примерами данных
    4. Изменять номер post (все поля сразу)
    5. Изменять номер patch (какие-то поля выборочно или все поля сразу)
    6. Удалять номер

Рабочие ссылки (список методов, параметры в подробном перечне):
get("/hotels/{hotel_id}/rooms/all") - Вывод для конкретного отеля списка 
        ВСЕХ номеров - весь список полностью.
        Функция: show_rooms_in_hotel_all_get

get("/hotels/{hotel_id}/rooms/free") - Вывод для конкретного отеля списка 
        СВОБОДНЫХ номеров - весь список полностью.
        Функция: show_rooms_in_hotel_free_get

get("/hotels/rooms/{room_id}") - Получение из базы данных выбранной 
        записи по идентификатору отеля.
        Функция: get_rooms_id_get

post("/hotels/room") - Создание записи с новой комнатой в отеле.
        Функция: create_room_post

delete("/hotels/rooms/{room_id}") - Удаление выбранной записи по 
        идентификатору номера.
        Реализовано удаление одного объекта, когда объект для удаления получаем 
        по первичному ключу (метод session.get), удаляем методом session.delete.
        Используются методы:
        - session.get(RoomsORM, id) для получения объекта по ключу
        - session.delete(room_object) для удаления объекта room_object.
        Функция: delete_room_id_del

delete("/hotels/rooms/") - Удаление выбранной записи по 
        идентификатору номера.
        При желании можно дополнить удаление по любым условиям, а не только по id.
        Удаление выбранных записей реализовано через метод delete.
        Функция: delete_rooms_del

put("/hotels/{hotel_id}/rooms/{room_id}") - Обновление ВСЕХ данных одновременно 
        для выбранной записи, выборка происходит по идентификатору номера.
        Обновление выбранных записей реализовано с использованием метода 
        session.get(RoomsORM, id) для получения объекта по ключу с последующие
        изменением нужных полей для полученного элемента.
        Функция: change_room_hotel_id_put

put("/hotels/rooms/{room_id}") - Обновление ВСЕХ данных одновременно 
        для выбранной записи, выборка происходит по идентификатору номера.
        При желании можно дополнить обновление нескольких записей по любым 
        условиям, а не только по id.
        Обновление выбранных записей реализовано через метод update.
        Функция: change_room_put

patch("/hotels/{hotel_id}/rooms/{room_id}") - Обновление каких-либо данных выборочно 
        или всех данных сразу для выбранной записи, выборка происходит по 
        идентификатору номера.
        Обновление выбранных записей реализовано с использованием метода 
        session.get(RoomsORM, id) для получения объекта по ключу с последующие
        изменением нужных полей для полученного элемента.
        Функция: change_room_hotel_id_patch

patch("/hotels/rooms/{room_id}") - Обновление каких-либо данных выборочно 
        или всех данных сразу для выбранной записи, выборка происходит по 
        идентификатору номера.
        При желании можно дополнить обновление нескольких записей по любым 
        условиям, а не только по id.
        Обновление выбранных записей реализовано через метод update.
        Функция: change_room_patch
"""

# Если в списке указывается несколько тегов, то для
# каждого тега создаётся свой раздел в документации
router = APIRouter(prefix="/hotels", tags=["Номера"])


openapi_examples_dict = {"1": {"summary": "Номер обычный (укажите правильное значение для hotel_id)",
                               "description": "Обязательно укажите правильное значение для hotel_id.<br>"
                                              "Значения в параметре facilities_ids можно не указывать, "
                                              "передать [].",
                               "value": {"hotel_id": 1,  # int, Идентификатор отеля, в котором находится комната
                                         "title": "Название обычного номера",  # String(length=100)
                                         "description": "Описание обычного номера",  # str
                                         "price": 11,  # int, Цена номера
                                         "quantity": 12,  # int, Общее количество номеров такого типа
                                         "facilities_ids": []  # list[int], Список из идентификаторов удобств
                                         }
                               },
                         "2": {"summary": "Люкс (укажите правильное значение для hotel_id)",
                               "description": "Тут тоже надо указать правильное значение для hotel_id.",
                               "value": {"hotel_id": 1,  # int, Идентификатор отеля, в котором находится комната
                                         "title": "Название люкса",  # String(length=100)
                                         "description": "Описание люкса",  # str
                                         "price": 21,  # int, Цена номера
                                         "quantity": 22,  # int, Общее количество номеров такого типа
                                         "facilities_ids": [1, 2]  # list[int], Список из идентификаторов удобств
                                         }
                               }
                         }


@router.post("/room",
             summary="Создание записи с новой комнатой в отеле",
             description="Тут будет описание параметров метода",
             )
async def create_room_post(room_params: Annotated[RoomDescriptionRecURL,
                                                  Body(openapi_examples=openapi_examples_dict)],
                                                  # Body()],
                           db: DBDep):
    """
    ## Функция создаёт запись.

    Параметры (передаются методом Body):
    - ***:param** title:* Название отеля (обязательно)
    - ***:param** location:* Местонахождение отеля (обязательно)

    ***:return:*** Словарь: `dict("status": status, "added data": added_hotel)`, где
        - *status*: str. Статус завершения операции.
        - *added_hotel*: HotelPydanticSchema. Запись с добавленными данными.
          Тип возвращаемых элементов преобразован к указанной схеме Pydantic.

    В текущей реализации статус завершения операции всегда один и тот же: OK
    """
    # Если нет отеля, имеющего в поле id значение, соответствующее
    # указанному в поле hotel_id, то возникает ошибка:
    # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError)
    #       <class 'asyncpg.exceptions.ForeignKeyViolationError'>:
    #       INSERT или UPDATE в таблице "rooms" нарушает ограничение внешнего ключа
    #       "rooms_hotel_id_fkey"
    # DETAIL:  Ключ (hotel_id)=(1) отсутствует в таблице "hotels".
    # [SQL: INSERT INTO rooms (hotel_id, title, description, price, quantity)
    #   VALUES ($1::INTEGER, $2::VARCHAR, $3::VARCHAR, $4::INTEGER, $5::INTEGER)
    #   RETURNING rooms.id, rooms.hotel_id, rooms.title,
    #             rooms.description, rooms.price, rooms.quantity]
    # [parameters: (1, 'Название номера', 'Описание номера', 2, 3)]
    # (Background on this error at: https://sqlalche.me/e/20/gkpj)

    # Если не указаны данные для поля, являющегося обязательным (в примере
    # искусственно в поле title установлено значение None), то возникает ошибка:
    # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError)
    #       <class 'asyncpg.exceptions.NotNullViolationError'>: значение NULL в столбце "title"
    #       отношения "rooms" нарушает ограничение NOT NULL
    # DETAIL:  Ошибочная строка содержит (23, 198, null, 198Описание обычного номера, 19811, 19812).
    # [SQL: INSERT INTO rooms (hotel_id, title, description, price, quantity)
    #   VALUES ($1::INTEGER, $2::VARCHAR, $3::VARCHAR, $4::INTEGER, $5::INTEGER)
    #   RETURNING rooms.id, rooms.hotel_id, rooms.title,
    #             rooms.description, rooms.price, rooms.quantity]
    # [parameters: (198, None, '198Описание обычного номера', 19811, 19812)]
    # (Background on this error at: https://sqlalche.me/e/20/gkpj)
    room_params_schema = RoomBase(**room_params.model_dump())
    room = await db.rooms.add(room_params_schema)
    # room имеет тип словарь из одного элемента: {"added rooms": item: RoomPydanticSchema}
    rooms_facilities_data = [RoomsFacilityBase(room_id=room["added rooms"].id,
                                               facility_id=f_id)
                             for f_id in room_params.facilities_ids]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()
    return {"added rooms": {**room["added rooms"].model_dump(),
                            "facilities_ids": room_params.facilities_ids,
                            }
            }


@router.get("/{hotel_id}/rooms/all",
            summary="Вывод для конкретного отеля списка ВСЕХ "
                    "номеров - весь список полностью",
            description="Тут будет описание параметров метода",
            )
# async def show_rooms_in_hotel_get(hotel_id: Path()):
async def show_rooms_in_hotel_all_get(hotel_path: Annotated[HotelPath, Path()],
                                      pagination: PaginationAllDep,
                                      db: DBDep):
    # return await db.rooms.get_all(hotel_id=hotel_path.hotel_id)
    return await db.rooms.get_limit(hotel_id=hotel_path.hotel_id,
                                    # Было RoomPydanticSchema, но так как подключаем получение
                                    # списка удобств, то схема их должна уметь распознавать
                                    pydantic_schema=RoomWithRels,
                                    per_page=pagination.per_page,
                                    page=pagination.page,
                                    show_all=pagination.all_objects,
                                    )


@router.get("/{hotel_id}/rooms/free",
            summary="Вывод для конкретного отеля списка СВОБОБНЫХ "
                    "номеров - весь список полностью",
            description="Тут будет описание параметров метода",
            )
# async def show_rooms_in_hotel_get(hotel_id: Path()):
async def show_rooms_in_hotel_free_get(hotel_path: Annotated[HotelPath, Path()],
                                       pagination: PaginationAllDep,
                                       db: DBDep,
                                       date_from: Annotated[date | None,
                                                            Query(example='2025-01-20',
                                                                  description="Дата, С которой бронируется номер",
                                                                  )] = None,
                                       date_to: Annotated[date | None,
                                                          Query(example='2025-01-23',
                                                                description="Дата, ДО которой бронируется номер",
                                                                )] = None
                                       ):
    # Параметр date_from - Дата, С которой бронируется номер.
    # Параметр date_to - Дата, ДО которой бронируется номер.
    # return await db.rooms.get_filtered_by_time(hotel_id=hotel_path.hotel_id,
    #                                            per_page=pagination.per_page,
    #                                            page=pagination.page,
    #                                            show_all=pagination.all_objects,
    #                                            date_from=date_from,
    #                                            date_to=date_to)
    return await db.rooms.get_limit(hotel_id=hotel_path.hotel_id,
                                    # Было RoomPydanticSchema, но так как подключаем получение
                                    # списка удобств, то схема их должна уметь распознавать
                                    pydantic_schema=RoomWithRels,
                                    per_page=pagination.per_page,
                                    page=pagination.page,
                                    show_all=pagination.all_objects,
                                    free_rooms=True,
                                    date_from=date_from,
                                    date_to=date_to,
                                    )


@router.get("/rooms/find",
            summary="Поиск отелей по заданным параметрам и "
                    "вывод итогового списка с разбивкой по страницам",
            description="Тут будет описание параметров метода",
            )
async def find_rooms_get(pagination: PaginationPagesDep,
                         db: DBDep,
                         title: Annotated[str | None, Query(min_length=3,
                                                            description="Наименование номера"
                                                            )] = None,
                         description: Annotated[str | None, Query(min_length=3,
                                                                  description="Описание номера",
                                                                  )] = None,
                         case_sensitivity: Annotated[bool | None,
                                                     Query(alias="case-sensitivity",
                                                           description="Поиск с учётом регистра "
                                                                       "(True) или регистронезависимый "
                                                                       "(False или None)",
                                                           )] = None,
                         starts_with: Annotated[bool | None,
                                                Query(alias="starts-with",
                                                      description="Поиск строк, начинающихся с "
                                                                  "заданного текста (True), или "
                                                                  "поиск строк, содержащих "
                                                                  "заданный текст (False или None)",
                                                      )] = None,
                         price_min: Annotated[int | None, Query(alias="price-min",
                                                                ge=0,
                                                                description="Минимальная цена номера",
                                                                )] = None,
                         price_max: Annotated[int | None, Query(alias="price-max",
                                                                ge=0,
                                                                description="Максимальная цена номера",
                                                                )] = None,
                         free_rooms: Annotated[bool | None,
                                               Query(alias="free-rooms",
                                                     description="Выбирать свободные (не забронированные) "
                                                                 "номера в указанные даты (True) "
                                                                 "или выбирать полный список номеров, "
                                                                 "не учитывая указанные даты"
                                                                 "(False или None)",
                                                     )] = None,
                         # date_from: date = Query(example='2025-01-20',
                         #                         description="Дата, С которой бронируется номер",
                         #                         default=None),
                         # date_to: date = Query(example='2025-01-23',
                         #                       description="Дата, ДО которой бронируется номер",
                         #                       default=None),
                         date_from: Annotated[date | None,
                                              Query(example='2025-01-20',
                                                    description="Дата, С которой бронируется номер",
                                                    )] = None,
                         date_to: Annotated[date | None,
                                            Query(example='2025-01-23',
                                                  description="Дата, ДО которой бронируется номер",
                                                  )] = None
                         ):
    """
    ## Функция ищет отели по заданным параметрам и выводит информацию о найденных отелях с разбивкой по страницам.

    Параметры:
    - ***:param** db:* Контекстный менеджер.

    Параметры (передаются методом Query):
    - ***:param** title:* Наименование номера (может отсутствовать).
    - ***:param** description:* Описание номера (может отсутствовать).
    - ***:param** case_sensitivity:* Поиск с учётом регистра (True) или
                регистронезависимый (False или None). Может отсутствовать.
    - ***:param** starts_with:* Поиск строк, начинающихся с заданного
                текста (True), или поиск строк, содержащих заданный текст
                (False или None). Может отсутствовать.
    - ***:param** page:* Номер страницы для вывода (должно быть >=1,
                по умолчанию значение 1).
    - ***:param** per_page:* Количество элементов на странице (должно быть
                >=1 и <=30, по умолчанию значение 3).
    - ***:param** price_min:* Минимальная цена номера (должно быть >=0,
                по умолчанию значение не задано - None). Может отсутствовать.
    - ***:param** price_max:* Максимальная цена номера (должно быть >=0,
                по умолчанию значение не задано - None). Может отсутствовать.
    - ***:param** free_rooms:* Выбирать свободные (не забронированные) номера
                в указанные даты (True) или выбирать полный список номеров,
                не учитывая указанные даты (False или None).
                Может отсутствовать.
    - ***:param** date_from:* Дата, С которой бронируется номер.
            Используется, если параметр hotels_with_free_rooms=True.
    - ***:param** date_to:* Дата, ДО которой бронируется номер.
            Используется, если параметр hotels_with_free_rooms=True.

    ***:return:*** Список отелей или строка с уведомлением, если список отель пуст.

    Один из двух параметров `title` или `description` обязан быть задан.

    Если переданы оба параметра `title` и `description`, то
    выбираться будет номер, соответствующий обоим параметрам одновременно.

    Указание цены (price_min и/или price_max) ограничивает вывод для ранее произведённого
    поиска по параметрам `title` и/или `description`.
    Только цену для поиска задавать пока нельзя, обязательно указывать один из двух
    параметров `title` или `description`.

    Значения `case_sensitivity` и `starts_with` влияют на поиск по обоим
    параметрам `title` и `description`.

    Список номеров выводится в виде:
    list(info: list(str, str),
         list(dict(room_item: RoomItem) | str)),
    где:
    - ***info***, это информация, какая страница выводится и сколько элементов на странице;
    - ***list(dict(room_item: RoomItem) | str)***, это список выводимых отелей или строка,
    что "Данные отсутствуют".
    Список номеров выводится в виде:
            [RoomPydanticSchema(hotel_id=26, title='title_string_1',
                                description='description_string_1',
                                price=1, quantity=1, id=32),
             RoomPydanticSchema(hotel_id=21, title='title_string_2',
                                description='description_string_2',
                                price=1, quantity=1, id=34),
             ..., RoomPydanticSchema(hotel_id=21, title='title_string_N',
                                     description='description_string_N',
                                     price=1, quantity=1, id=38)]
             Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
    """

    query = await db.rooms.create_stmt_for_selection(sql_func=sa_select,
                                                     title={"search_string": title,
                                                            "case_sensitivity": case_sensitivity,
                                                            "starts_with": starts_with},
                                                     description={"search_string": description,
                                                                  "case_sensitivity": case_sensitivity,
                                                                  "starts_with": starts_with},
                                                     order_by=True,
                                                     )
    # if hotels_with_free_rooms:
    #     # Выбирать отели со свободными номерами в указанные даты (True)
    #     if not (date_from and date_to):
    #         # status_code=422: Запрос сформирован правильно, но его невозможно
    #         #                  выполнить из-за семантических ошибок
    #         #                  Unprocessable Content (WebDAV)
    #         raise HTTPException(status_code=422,
    #                             detail={"description": "Не заданы даты для выбора "
    #                                                    "отелей со свободными номерами",
    #                                     })
    # else:
    #     date_from = None,
    #     date_to = None

    return await db.rooms.get_limit(query=query,
                                    # Было RoomPydanticSchema, но так как подключаем получение
                                    # списка удобств, то схема их должна уметь распознавать
                                    pydantic_schema=RoomWithRels,
                                    per_page=pagination.per_page,
                                    page=pagination.page,
                                    free_rooms=free_rooms,
                                    date_from=date_from,
                                    date_to=date_to,
                                    price_min=price_min,
                                    price_max=price_max,
                                    )


@router.get("/rooms/{room_id}/session_get",
            summary="Получение из базы данных выбранной записи по идентификатору "
                    "номера, используя метод session.get(model, object_id)",
            description="Тут будет описание параметров метода",
            )
async def get_room_session_get_method_get(room: Annotated[RoomPath, Path()], db: DBDep):
    """
    ## Функция получает из базы данных выбранную запись по идентификатору отеля.

    Параметры:
    :param db: Контекстный менеджер.

    Параметры (передаются в URL):
    :param room: Идентификатор номера (обязательно): room.room_id.

    :return: Возвращает словарь: {"room": dict},
        где:
        - room: Выбранный объект.
            Тип возвращаемого элемента преобразован к схеме Pydantic: RoomWithRels.
            Поле facilities содержит список удобств (id, title) или пустой список ([]).
        Если номер не найден, то возбуждается исключение 404.
    """
    result = await db.rooms.get_by_id(room_id=room.room_id)
    return result


@router.get("/rooms/{room_id}/session_execute",
            summary="Получение из базы данных выбранной записи по идентификатору номера, "
                    "используя метод session.execute(select(model).filter_by(**filtering))",
            description="Тут будет описание параметров метода",
            )
async def get_room_session_execute_method_get(room: Annotated[RoomPath, Path()], db: DBDep):
    """
    ## Функция получает из базы данных выбранную запись по идентификатору отеля.

    Параметры:
    :param db: Контекстный менеджер.

    Параметры (передаются в URL):
    :param room: Идентификатор номера (обязательно): room.room_id.

    :return: Возвращает словарь: {"room": dict},
        где:
        - room: Выбранный объект.
            Тип возвращаемого элемента преобразован к схеме Pydantic: RoomWithRels.
            Поле facilities содержит список удобств (id, title) или пустой список ([]).
        Если номер не найден, то возбуждается исключение 404.
    """
    result = await db.rooms.get_by_id_one_or_none(room_id=room.room_id)
    return result


@router.delete("/rooms/{room_id}",
               summary="Удаление выбранной записи по идентификатору номера",
               description="Тут будет описание параметров метода",
               )
# async def delete_hotel_id_del(hotel: Annotated[HotelPath, Path()]):
async def delete_room_id_del(room: Annotated[RoomPath, Path()], db: DBDep):
    """
    ## Функция удаляет выбранную запись.

    Параметры (передаются в URL):
    - ***:param** hotel_id:* Идентификатор отеля (обязательно).

    ***:return:*** Словарь: `{"status": str, "deleted": str | dict}`, где:

    - ***status***: статус операции (реализованы варианты: OK и Error);
    - ***deleted***: это список выводимых отелей в формате:
    `list(dict("id": hotel.id, "title": hotel.title, "location": hotel.location))`
    или информационная строка.

    В текущей реализации статус завершения операции всегда один и тот же: OK

    Если работать с БД, то добавятся новые статусы.
    """

    result = await db.rooms.delete_id(room_id=room.room_id)
    await db.commit()  # Подтверждаем изменение
    return result


@router.delete("/rooms/",
               summary="Удаление выбранных записей с выборкой по наименованию "
                       "и описанию номера - что требуется удалять",
               description="Тут будет описание параметров метода",
               )
# async def delete_hotel_id_del(hotel: Annotated[HotelPath, Path()]):
async def delete_rooms_param_del(db: DBDep,
                                 title: Annotated[str | None, Query(min_length=3,
                                                                    description="Наименование номера"
                                                                    )] = None,
                                 description: Annotated[str | None, Query(min_length=3,
                                                                          description="Описание номера",
                                                                          )] = None,
                                 case_sensitivity: Annotated[bool | None,
                                                             Query(alias="case-sensitivity",
                                                                   description="Поиск с учётом регистра "
                                                                               "(True) или регистронезависимый "
                                                                               "(False или None)",
                                                                   )] = None,
                                 starts_with: Annotated[bool | None,
                                                        Query(alias="starts-with",
                                                              description="Поиск строк, начинающихся с "
                                                                          "заданного текста (True), или "
                                                                          "поиск строк, содержащих "
                                                                          "заданный текст (False или None)",
                                                              )] = None,
                                 ):
    """
    ## Функция удаляет выбранную запись или записи с выборкой, что удалять, по наименованию и описанию номера.

    Параметры:
    - ***:param** db:* Контекстный менеджер.

    Параметры (передаются методом Query):
    - ***:param** title:* Наименование номера (может отсутствовать).
    - ***:param** description:* Описание номера (может отсутствовать).
    - ***:param** case_sensitivity:* Поиск с учётом регистра (True) или
                регистронезависимый (False или None). Может отсутствовать.
    - ***:param** starts_with:* Поиск строк, начинающихся с заданного
                текста (True), или поиск строк, содержащих заданный текст
                (False или None). Может отсутствовать.

        :return: Возвращает словарь:
            {"deleted rooms": list(dict)},
            где:
            - deleted_hotels: Список с удалёнными элементами:
                  [RoomPydanticSchema(hotel_id=26, title='title_string_1',
                                      description='description_string_1',
                                      price=1, quantity=1, id=32),
                   RoomPydanticSchema(hotel_id=21, title='title_string_2',
                                      description='description_string_2',
                                      price=1, quantity=1, id=34),
                   ..., RoomPydanticSchema(hotel_id=21, title='title_string_N',
                                           description='description_string_N',
                                           price=1, quantity=1, id=38)]
                  Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema

        Если элементы, соответствующие запросу на удаление в параметре delete_stmt
        и фильтрам, указанным в **filtering, отсутствуют, возбуждается исключение
        HTTPException с кодом 404.

    Один из двух параметров `title` или `description` обязан быть задан.

    Значения `case_sensitivity` и `starts_with` влияют на поиск по обоим
    параметрам `title` и `description`.

    Если переданы оба параметра `title` и `description`, то
    выбираться будет номер, соответствующий обоим параметрам одновременно.
    """

    stmt = await db.rooms.create_stmt_for_selection(sql_func=sa_delete,
                                                    title={"search_string": title,
                                                           "case_sensitivity": case_sensitivity,
                                                           "starts_with": starts_with},
                                                    description={"search_string": description,
                                                                 "case_sensitivity": case_sensitivity,
                                                                 "starts_with": starts_with},
                                                    )

    result = await db.rooms.delete(delete_stmt=stmt)
    await db.commit()  # Подтверждаем изменение
    print(result)
    return result


change_room_examples_lst = [{"hotel_id": 1,  # int, Идентификатор отеля, в котором находится комната
                             "title": "Название номера - put",  # String(length=100)
                             "description": "Описание номера - put",  # str
                             "price": 2,  # int, Цена номера
                             "quantity": 3,  # int, Общее количество номеров такого типа
                             "facilities_ids": []  # list[int] | [], Список из идентификаторов удобств
                             },
                            ]


@router.put("/{hotel_id}/rooms/{room_id}",
            summary="Обновление ВСЕХ данных одновременно для выбранной "
                    "записи, выборка происходит по идентификатору номера",
            description="Тут будет описание параметров метода",
            )
# async def change_room_hotel_id_put(hotel: Annotated[HotelPath, Path()],
#                                    room: Annotated[RoomPath, Path()],
#                                    room_params: Annotated[RoomDescrRecRequest,
#                                                           Body()],
#                                    ):
async def change_room_hotel_id_put(hotel_room: Annotated[HotelRoomPath, Path()],
                                   room_params: Annotated[RoomDescrRecRequest,
                                                          Body()],
                                   db: DBDep,
                                   ):
    # В исходных данных приходит поле facilities_ids, которое отсутствует в таблице
    # Поэтому надо полученный набор полей преобразовать к схеме RoomBase.
    _room_params = RoomBase(**room_params.model_dump(),
                            hotel_id=hotel_room.hotel_id)

    # result = await db.rooms.edit(edited_data=_room_params,
    #                              id=hotel_room.room_id)

    # Редактируем таблицу с номерами
    result = await db.rooms.edit_id(edited_data=_room_params,
                                    room_id=hotel_room.room_id)

    # Редактируем m2m таблицу номера-удобства
    await db.rooms_facilities.set_facilities_in_rooms_values(room_id=hotel_room.room_id,
                                                             facilities_ids=room_params.facilities_ids)

    await db.commit()  # Подтверждаем изменение
    # Вариант вместо блока async with async_session_maker() as session:
    # то есть, обращаемся к уже написанной функции change_room_put.
    # Этот вариант может быть хорош, если функция делает какую-то
    # дополнительную обработку.
    # room = RoomPath(room_id=hotel_room.room_id)
    # result = await change_room_put(room=room, room_params=_room_params)
    return result


@router.put("/rooms/{room_id}",
            summary="Обновление ВСЕХ данных одновременно для выбранной "
                    "записи, выборка происходит по идентификатору номера",
            description="Тут будет описание параметров метода",
            )
async def change_room_put(room: Annotated[RoomPath, Path()],
                          room_params: Annotated[RoomDescriptionRecURL,
                                                 # Body(examples=change_room_examples_lst)],
                                                 Body()],
                          db: DBDep,
                          ):
    """
    ## Функция изменяет (обновляет) ВСЕ данные одновременно

    В ручке PUT мы обязаны передать сразу все параметры (hotel_id,
    title, description, price, quantity).

    Параметры (передаются в URL):
    - ***:param** room_id:* Идентификатор отеля (обязательно).

    Параметры (передаются методом Body):
    - ***:param** hotel_id:* Идентификатор отеля, в котором находится комната (обязательно).
    - ***:param** title:* Название номера (обязательно).
    - ***:param** description:* Описание номера (обязательно).
    - ***:param** price:* Цена номера (обязательно).
    - ***:param** quantity:* Общее количество номеров такого типа (обязательно).

    ***:return:*** Возвращает словарь:
                {"status": status, "err_type": err_type, "updated rows": updated_rows},
                где:
                - status: str. Текстовое описание результата операции.
                - err_type: int. Код результата операции.
                  Принимает значения:
                  - 0 (OK - выполнено нормально, без ошибок).
                  - 1 (Для объекта с указанным идентификатором ничего не найдено).
                - updated_rows. Список, содержащий отредактированный объект. Выводится
                  в виде списка, содержащего элементы объекта RoomsORM.


    Значение статуса завершения операции:
    - 0: все OK.
    - 1: ничего не найдено.
    """
    # В исходных данных приходит поле facilities_ids, которое отсутствует в таблице
    # Поэтому надо полученный набор полей преобразовать к схеме RoomBase.

    # Редактируем таблицу с номерами
    result = await db.rooms.edit(edited_data=RoomBase(**room_params.model_dump()),
                                 id=room.room_id)
    # result = await db.rooms.edit_id(edited_data=room_params,
    #                                 room_id=room.room_id)

    # Редактируем m2m таблицу номера-удобства
    await db.rooms_facilities.set_facilities_in_rooms_values(room_id=room.room_id,
                                                             facilities_ids=room_params.facilities_ids)
    await db.commit()  # Подтверждаем изменение
    return result


change_room_examples_lst = [{"hotel_id": 1,  # int, Идентификатор отеля, в котором находится комната
                             "title": "Название номера - patch",  # String(length=100)
                             "description": "Описание номера - patch",  # str
                             "price": 2,  # int, Цена номера
                             "quantity": 3,  # int, Общее количество номеров такого типа
                             "facilities_ids": []  # list[int] | [], Список из идентификаторов удобств
                             },
                            ]
openapi_examples_dict = {"full": {"summary": "A normal example",
                                  "description": "A **normal** item works correctly.",
                                  "value": {"hotel_id": 1,  # int, Идентификатор отеля, в котором находится комната
                                            "title": "Название номера - patch",  # String(length=100)
                                            "description": "Описание номера - patch",  # str
                                            "price": 2,  # int, Цена номера
                                            "quantity": 3,  # int, Общее количество номеров такого типа
                                            "facilities_ids": []  # list[int] | [], Список из идентификаторов удобств
                                            }
                                  },
                         "without facilities_ids": {"summary": "Example without facilities_ids",
                                                    "description": "A **without facilities_ids** item works correctly.",
                                                    "value": {"hotel_id": 1,  # int, Идентификатор отеля, в котором находится комната
                                                              "title": "Название номера - patch",  # String(length=100)
                                                              "description": "Описание номера - patch",  # str
                                                              "price": 2,  # int, Цена номера
                                                              "quantity": 3,  # int, Общее количество номеров такого типа
                                                              # "facilities_ids": []  # list[int] | [], Список из идентификаторов удобств
                                                              }
                                                    },
                         }


@router.patch("/{hotel_id}/rooms/{room_id}",
              summary="Обновление каких-либо данных выборочно или всех данных сразу "
                      "для выбранной записи, выборка происходит по идентификатору номера",
              description="Тут будет описание параметров метода",
              )
# async def change_room_hotel_id_patch(room: Annotated[RoomPath, Path(examples=[{"hotel_id": 1}])],
#                                      room_params: Annotated[RoomDescriptionOptURL,
#                                                             Body()],
#                                      ):
async def change_room_hotel_id_patch(hotel_room: Annotated[HotelRoomPath, Path()],
                                     room_params: Annotated[RoomDescrOptRequest,
                                                            Body()],
                                     db: DBDep,
                                     ):

    # В исходных данных приходит поле facilities_ids, которое отсутствует в таблице
    # Поэтому надо полученный набор полей преобразовать к схеме RoomBase.
    # _room_params = RoomDescriptionOptURL(hotel_id=hotel_room.hotel_id,
    _room_params = RoomBase(hotel_id=hotel_room.hotel_id,
                            **room_params.model_dump(exclude_unset=True))
    # result = await db.rooms.edit(edited_data=_room_params,
    #                              id=hotel_room.room_id,
    #                              exclude_unset=True)

    # Редактируем таблицу с номерами
    result = await db.rooms.edit_id(edited_data=_room_params,
                                    room_id=hotel_room.room_id,
                                    exclude_unset=True)

    # Редактируем m2m таблицу номера-удобства
    room_params_dict = room_params.model_dump(exclude_unset=True)
    if "facilities_ids" in room_params_dict:
        # Проверять надо room_params_dict["facilities_ids"], а не room_params.facilities_ids
        # так как если клиент не будет передавать поле facilities_ids, то в
        # room_params.facilities_ids будет приходить значение по умолчанию - так как
        # клиент его не изменял и не передавал.
        await db.rooms_facilities.set_facilities_in_rooms_values(room_id=hotel_room.room_id,
                                                                 facilities_ids=room_params_dict["facilities_ids"])

    await db.commit()  # Подтверждаем изменение
    # Вариант вместо блока async with async_session_maker() as session:
    # то есть, обращаемся к уже написанной функции change_room_put.
    # Этот вариант может быть хорош, если функция делает какую-то
    # дополнительную обработку.
    # room = RoomPath(room_id=hotel_room.room_id)
    # result = await change_room_patch(room=room, room_params=_room_params)
    return result


@router.patch("/rooms/{room_id}",
              summary="Обновление каких-либо данных выборочно или всех данных сразу "
                      "для выбранной записи, выборка происходит по идентификатору номера",
              description="Тут будет описание параметров метода",
              )
async def change_room_patch(room: Annotated[RoomPath, Path(examples=[{"hotel_id": 1}])],
                            room_params: Annotated[RoomDescriptionOptURL,
                                                   Body(examples=change_room_examples_lst,
                                                        openapi_examples=openapi_examples_dict)],
                                                   # Body()],
                            db: DBDep,
                            ):
    """
    ## Функция обновляет каких-либо данные выборочно или все данных сразу

    В PATCH ручке можем передать какие-либо из параметров (hotel_id, title,
    description, price, quantity) в произвольном сочетании, либо все
    параметры сразу (тогда PATCH ручка ничем не отличается от PUT ручки).

    Параметры (передаются в URL):
    - ***:param** room_id:* Идентификатор отеля (обязательно).

    Параметры (передаются методом Body):
    - ***:param** hotel_id:* Идентификатор отеля, в котором находится
            комната (необязательно, не указан - изменяться не будет).
    - ***:param** title:* Название номера (необязательно, не
            указан - изменяться не будет).
    - ***:param** description:* Описание номера (необязательно, не
            указан - изменяться не будет).
    - ***:param** price:* Цена номера (необязательно, не
            указан - изменяться не будет).
    - ***:param** quantity:* Общее количество номеров такого типа
            (необязательно, не указан - изменяться не будет).

    ***:return:*** Возвращает словарь:
                {"status": status, "err_type": err_type, "updated rows": updated_rows},
                где:
                - status: str. Текстовое описание результата операции.
                - err_type: int. Код результата операции.
                  Принимает значения:
                  - 0 (OK - выполнено нормально, без ошибок).
                  - 1 (Для объекта с указанным идентификатором ничего не найдено).
                - updated_rows. Список, содержащий отредактированный объект. Выводится
                  в виде списка, содержащего элементы объекта RoomsORM.


    Значение статуса завершения операции:
    - 0: все OK.
    - 1: ничего не найдено.
    """
    # В исходных данных приходит поле facilities_ids, которое отсутствует в таблице
    # Поэтому надо полученный набор полей преобразовать к схеме RoomBase.

    # Редактируем таблицу с номерами
    result = await db.rooms.edit(edited_data=RoomBase(**room_params.model_dump()),
                                 id=room.room_id,
                                 exclude_unset=True)
    # result = await db.rooms.edit_id(edited_data=room_params,
    #                                 room_id=room.room_id,
    #                                 exclude_unset=True)

    # Редактируем m2m таблицу номера-удобства
    room_params_dict = room_params.model_dump(exclude_unset=True)
    if "facilities_ids" in room_params_dict:
        # Проверять надо room_params_dict["facilities_ids"], а не room_params.facilities_ids
        # так как если клиент не будет передавать поле facilities_ids, то в
        # room_params.facilities_ids будет приходить значение по умолчанию - так как
        # клиент его не изменял и не передавал.
        await db.rooms_facilities.set_facilities_in_rooms_values(room_id=room.room_id,
                                                                 facilities_ids=room_params_dict["facilities_ids"])
    await db.commit()  # Подтверждаем изменение
    return result
