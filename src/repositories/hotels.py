from datetime import date
from typing import Union, Callable, Any

from fastapi import HTTPException
from pydantic import BaseModel

from sqlalchemy import func as sa_func

from sqlalchemy import select as sa_select  # Для реализации SQL команды SELECT
from sqlalchemy import delete as sa_delete  # Для реализации SQL команды DELETE
from sqlalchemy import update as sa_update  # Для реализации SQL команды UPDATE
from sqlalchemy import insert as sa_insert  # Для реализации SQL команды INSERT

from sqlalchemy import Select as sa_Select  # Тип функции sa_select
from sqlalchemy import Delete as sa_Delete  # Тип функции sa_delete
from sqlalchemy import Update as sa_Update  # Тип функции sa_update
from sqlalchemy import Insert as sa_Insert  # Тип функции sa_insert


from sqlalchemy.exc import MultipleResultsFound

from src.repositories.base import BaseRepository
from src.repositories.utils import rooms_ids_for_booking_query

from src.models.rooms import RoomsORM
from src.models.hotels import HotelsORM

from src.schemas.hotels import HotelPydanticSchema

# from src.database import engine

# engine нужен, чтобы использовать диалект SQL:
# add_stmt = (sa_insert(self.model)
#             # .returning(self.model)
#             .values(**added_data.model_dump()
#                     )
#             )
# print(add_stmt.compile(compile_kwargs={"literal_binds": True}))
# # Вывод: INSERT INTO hotels (title, location)
# #        VALUES ('title_string', 'location_string')
# print(add_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
# # Вывод: INSERT INTO hotels (title, location)
# #        VALUES ('title_string', 'location_string')
# #        RETURNING hotels.id


class HotelsRepository(BaseRepository):
    model = HotelsORM
    schema = HotelPydanticSchema

    # Сделаны методы:
    #
    # - get_all. Выбирает все строки по всем отелям.
    #       Использует родительский метод get_rows.
    # - get_filtered_by_time. Выбирает все отели, в которых имеются свободные
    #       номера в указанный промежуток времени (от date_from до date_to).
    #       Использует родительский метод get_rows.
    # - create_stmt_for_selection. Формирует запрос для удаления или для
    #       выборки строк, в зависимости от переданного метода sa_select, sa_delete
    # - get_limit. Выбирает заданное количество строк с заданным смещением.
    #       Использует родительский метод get_rows.
    # - get_one_or_none_my_err. Возвращает одну строку или None. Если получено
    #       более одной строки, то поднимается исключение MultipleResultsFound.
    #       Использует родительский метод get_rows.
    # - edit. Редактирует один объект в базе, используя метод update.
    #       Служит обёрткой для родительского метода edit.
    # - delete. Удаляет объект или объекты в базе, используя метод delete.
    #       Служит обёрткой для родительского метода delete.
    # - get_id. Выбирает по идентификатору (поле self.model.id) один объект
    #       в базе, используя метод get.
    #       Служит обёрткой для родительского метода get_id.

    async def get_all(self):
        """
        Метод класса. Выбирает все строки по всем отелям.
            Использует родительский метод get_rows.
        :return: Возвращает список из выбранных строк:
            [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
             HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
             ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]

            Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema

        Если элементы отсутствуют, возбуждается исключение HTTPException с кодом 404.
        """
        result = await super().get_rows(show_all=True)
        # Возвращает пустой список: [] или список:
        # [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
        #  HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
        #  ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        if len(result) == 0:
            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            raise HTTPException(status_code=404,
                                detail={"description": "Данные отсутствуют.",
                                        })
        status = ("Полный список отелей.",
                  f"Всего выводится {len(result)} элемент(-а/-ов) на странице.")
        return {"status": status, "hotels": result}

    async def get_filtered_by_time(self,
                                   date_from: date,
                                   date_to: date,
                                   ):
        """
        Метод класса. Выбирает все отели, в которых имеются свободные номера
            в указанный промежуток времени (от date_from до date_to).
        Использует родительский метод get_rows.

        :param date_from: Дата, С которой бронируется номер.
        :param date_to: Дата, ДО которой бронируется номер.
        :return: Возвращает SQL-запрос для выборки отелей, имеющих свободные номера.
        """

        rooms_ids_to_get = rooms_ids_for_booking_query(date_from=date_from,
                                                       date_to=date_to)
        # print(hotels_ids_to_get.compile(compile_kwargs={"literal_binds": True}))
        # Запрос такой (выбирает room_id для свободных номеров,
        # таблица состоит из одного столбца room_id):
        # WITH rooms_count AS (
        #     --Получаем количество брони в период с date_from до date_to
        #     --То есть, это ЗАНЯТЫЕ номера
        #     --Выводятся столбцы: room_id и rooms_booked
        #     SELECT bookings.room_id AS room_id,
        #                count('*') AS rooms_booked
        #         FROM bookings
        #         WHERE bookings.date_from <= '2025-01-23'
        #               AND
        #               bookings.date_to >= '2025-01-20'
        #         GROUP BY bookings.room_id
        # ),
        #     rooms_left_table AS (
        #     --Получаем количество свободных номеров.
        #     --Выводятся столбцы: room_id и rooms_left
        #     --rooms_left может иметь значения >= 0.
        #         SELECT rooms.id AS room_id,
        #                rooms.quantity - coalesce(rooms_count.rooms_booked, 0) AS rooms_left
        #         FROM rooms
        #         LEFT OUTER JOIN rooms_count ON rooms.id = rooms_count.room_id
        # )
        # --Выбираем значения, в которых rooms_left > 0 - то есть, положительное, не равное нулю
        # SELECT rooms_left_table.room_id
        # FROM rooms_left_table
        # WHERE rooms_left_table.rooms_left > 0 AND
        #       rooms_left_table.room_id IN (SELECT rooms_ids_for_hotel.id
        #                                    FROM (SELECT rooms.id AS id
        #                                          FROM rooms) AS rooms_ids_for_hotel)
        hotels_ids_to_get = (sa_select(RoomsORM.hotel_id)
                             .select_from(RoomsORM)
                             .filter(RoomsORM.id.in_(rooms_ids_to_get)))
        # print(hotels_ids_to_get.compile(compile_kwargs={"literal_binds": True}))
        # Запрос такой (выбирает hotel_id, содержащие свободные
        # номера, таблица состоит из одного столбца hotel_id):
        # WITH rooms_count AS (
        #         SELECT bookings.room_id AS room_id,
        #                count('*') AS rooms_booked
        #         FROM bookings
        #         WHERE bookings.date_from <= '2025-01-23' AND
        #               bookings.date_to >= '2025-01-20'
        #         GROUP BY bookings.room_id
        # ),
        #     rooms_left_table AS (
        #         SELECT rooms.id AS room_id,
        #                rooms.quantity - coalesce(rooms_count.rooms_booked, 0) AS rooms_left
        #         FROM rooms
        #         LEFT OUTER JOIN rooms_count ON rooms.id = rooms_count.room_id
        # )
        # SELECT rooms.hotel_id
        # FROM rooms
        # WHERE rooms.id IN (SELECT rooms_left_table.room_id
        #                    FROM rooms_left_table
        #                    WHERE rooms_left_table.rooms_left > 0 AND
        #                          rooms_left_table.room_id IN (SELECT rooms_ids_for_hotel.id
        #                                                       FROM (SELECT rooms.id AS id
        #                                                             FROM rooms) AS rooms_ids_for_hotel))

        # HotelsORM.id.in_(hotels_ids_to_get) - выбирает строки, в которых
        # HotelsORM.id содержится среди множества отелей hotels_ids_to_get.
        # В hotels_ids_to_get содержатся идентификаторы отелей, в которых
        # имеются свободные номера.

        # Tакой вызов был ранее:
        # return await self.get_filtered(HotelsORM.id.in_(hotels_ids_to_get))

        # print(HotelsORM.id.in_(hotels_ids_to_get).compile(compile_kwargs={"literal_binds": True}))
        # Итоговый запрос:
        # hotels.id IN (WITH rooms_count AS (
        #                      SELECT bookings.room_id AS room_id,
        #                             count('*') AS rooms_booked
        #                      FROM bookings
        #                      WHERE bookings.date_from <= '2025-01-23'
        #                            AND
        #                            bookings.date_to >= '2025-01-20'
        #                      GROUP BY bookings.room_id
        #              ),
        #                  rooms_left_table AS (
        #                      SELECT rooms.id AS room_id,
        #                             rooms.quantity - coalesce(rooms_count.rooms_booked, 0) AS rooms_left
        #                      FROM rooms
        #                      LEFT OUTER JOIN rooms_count ON rooms.id = rooms_count.room_id
        #              )
        #              SELECT rooms.hotel_id
        #              FROM rooms
        #              WHERE rooms.id IN (SELECT rooms_left_table.room_id
        #                                 FROM rooms_left_table
        #                                 WHERE rooms_left_table.rooms_left > 0
        #                                       AND
        #                                       rooms_left_table.room_id
        #                                 IN (SELECT rooms_ids_for_hotel.id
        #                                     FROM (SELECT rooms.id AS id
        #                                           FROM rooms) AS rooms_ids_for_hotel)
        #                                     )
        #                                 )
        return HotelsORM.id.in_(hotels_ids_to_get)

    sql_func_type = Callable[[Union[sa_select, sa_delete, sa_update, sa_insert]
                              ],
                             Union[sa_Select, sa_Delete, sa_Update, sa_Insert]
                             ]

    async def create_stmt_for_selection(self,
                                        location: dict[str | None,
                                                       bool | None,
                                                       bool | None],
                                        title: dict[str | None,
                                                    bool | None,
                                                    bool | None],
                                        sql_func: sql_func_type = sa_select,
                                        order_by=False,
                                        ):
        """
        Метод класса. Формирует запрос для удаления или для
            выборки строк, в зависимости от переданного метода sa_select, sa_delete.

        :param sql_func: Тип формируемого запроса.
            Принимает значения:
            - sqlalchemy.select. Исходный запрос формируется:
                hotels_stmt = select(self.model)
            - sqlalchemy.delete. Исходный запрос формируется:
                hotels_stmt = delete(self.model)

        :param location: Словарь с параметрами для формирования поиска по
            адресу отеля - по полю location.
            Параметр обязательный, словарь должен иметь вид:
            location: {"search_string": str | None = None,
                       "case_sensitivity": bool | None = None,
                       "starts_with": bool | None = None, }
            location["search_string"] - Строка для поиска по адресу отеля
            location["case_sensitivity"] - Поиск с учётом регистра (True) или
                регистронезависимый поиск (False или None). Может отсутствовать
            location["starts_with"] - Поиск строк, начинающихся с заданного
                текста (True), или поиск строк, содержащих заданный текст
                (False или None).

            Если не задано значение для параметра location или не задано значение
            location["search_string"] - поиск по адресу отеля не производится.

        :param title: Словарь с параметрами для формирования поиска по
            наименованию отеля - по полю title.
            Параметр обязательный, словарь должен иметь вид:
            title: {"search_string": str | None = None,
                    "case_sensitivity": bool | None = None,
                    "starts_with": bool | None = None, }
            title["search_string"] - Строка для поиска по наименованию отеля
            title["case_sensitivity"] - Поиск с учётом регистра (True) или
                регистронезависимый поиск (False или None). Может отсутствовать
            title["starts_with"] - Поиск строк, начинающихся с заданного
                текста (True), или поиск строк, содержащих заданный текст
                (False или None).

            Если не задано значение для параметра title или не задано значение
            title["search_string"] - поиск по наименованию отеля не производится.

        :param order_by: Добавить упорядочивание результатов (True) или нет (False или None).


        :return: Возвращает SQL-запрос с добавленными параметрами для поиска по
            адресу и наименованию отеля или SQL-запрос выбирающий все данные.
        """

        if not (location.get("search_string", False)
                or
                title.get("search_string", False)):
            # status_code=422: Запрос сформирован правильно, но его невозможно
            #                  выполнить из-за семантических ошибок
            #                  Unprocessable Content (WebDAV)
            raise HTTPException(status_code=422,
                                detail={"description": "Не заданы параметры для выбора отеля",
                                        })

        hotels_stmt = sql_func(self.model)
        # В зависимости от значения sql_func переменная hotels_stmt принимает значения:
        # - sql_func: sa_select
        #   hotels_stmt: SELECT hotels.id, hotels.title, hotels.location
        #                FROM hotels
        # - sql_func: sa_delete
        #   hotels_stmt: DELETE FROM hotels

        # location: {"search_string": None,         # Строка для поиска
        #            "case_sensitivity": None,      # Поиск с учётом регистра (True)
        #            "starts_with": None, }         # Поиск строк, начинающихся с заданного текста (True)
        search_string = location.get("search_string", "")
        if search_string:
            starts_with = '' if location.get("starts_with", False) else '%'
            if location.get("case_sensitivity", False):  # по умолчанию - None
                hotels_stmt = (hotels_stmt
                               .where(self.model.location.like(starts_with + search_string + "%"))
                               )
                # print(hotels_stmt.compile(compile_kwargs={"literal_binds": True}))

                # Параметр sql_func: sa_select
                # hotels_stmt: SELECT hotels.id, hotels.title, hotels.location
                #              FROM hotels
                #              WHERE hotels.location LIKE :location_1
                # или
                # Параметр sql_func: sa_delete
                # hotels_stmt: DELETE FROM hotels WHERE hotels.location LIKE :location_1

            else:
                hotels_stmt = (hotels_stmt
                               .where(self.model.location.ilike(starts_with + search_string + "%"))
                               )
                # print(hotels_stmt.compile(compile_kwargs={"literal_binds": True}))
                # Параметр sql_func: sa_select
                # hotels_stmt: SELECT hotels.id, hotels.title, hotels.location
                #              FROM hotels
                #              WHERE lower(hotels.location) LIKE lower(:location_1)
                # или
                # Параметр sql_func: sa_delete
                # hotels_stmt: DELETE FROM hotels WHERE lower(hotels.location) LIKE lower(:location_1)

        # title: {"search_string": None,         # Строка для поиска
        #         "case_sensitivity": None,      # Поиск с учётом регистра (True)
        #         "starts_with": None, }         # Поиск строк, начинающихся с заданного текста (True)
        search_string = title.get("search_string", "")
        if search_string:
            starts_with = '' if title.get("starts_with", False) else '%'
            if title.get("case_sensitivity", False):  # по умолчанию - None
                hotels_stmt = (hotels_stmt
                               .where(self.model.title.like(starts_with + search_string + "%"))
                               )
                # print(hotels_stmt.compile(compile_kwargs={"literal_binds": True}))
                # SELECT hotels.id, hotels.title, hotels.location
                # FROM hotels
                # WHERE hotels.title LIKE :title_1
                # или такой запрос (сочетание поиска с учётом регистра может быть разным):
                # SELECT hotels.id, hotels.title, hotels.location
                # FROM hotels
                # WHERE hotels.location LIKE :location_1 AND hotels.title LIKE :title_1
            else:
                hotels_stmt = (hotels_stmt
                               .where(self.model.title.ilike(starts_with + search_string + "%"))
                               )
                # print(hotels_stmt.compile(compile_kwargs={"literal_binds": True}))
                # SELECT hotels.id, hotels.title, hotels.location
                # FROM hotels
                # WHERE lower(hotels.title) LIKE lower(:title_1)
                # или такой запрос (сочетание поиска с учётом регистра может быть разным):
                # SELECT hotels.id, hotels.title, hotels.location
                # FROM hotels
                # WHERE lower(hotels.location) LIKE lower(:location_1) AND lower(hotels.title) LIKE lower(:title_1)

        if order_by:
            hotels_stmt = hotels_stmt.order_by(self.model.id)
            # print(hotels_stmt.compile(compile_kwargs={"literal_binds": True}))

        # print("Итоговый запрос:\n", hotels_stmt.compile(compile_kwargs={"literal_binds": True}))

        return hotels_stmt

    async def get_limit(self,
                        *filter,
                        query: sa_Select | None = None,
                        title: str | None = None,
                        location: str | None = None,
                        per_page: int | None = None,
                        page: int | None = None,
                        show_all: bool | None = None,
                        hotels_with_free_rooms: bool | None = None,
                        date_from: date | None = None,
                        date_to: date | None = None,
                        **filter_by,
                        ):
        """
        Метод класса. Выбирает заданное количество строк с
        заданным смещением. Использует родительский метод get_rows.

        :param filter: Фильтры для запроса - конструкция .filter(*filter).
        :param query: SQL-Запрос. Если простой SELECT-запрос на выборку,
            то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :param title: Наименование отеля
        :param location: Адрес отеля
        :param per_page: Количество элементов на странице (должно быть >=1 и
            <=30, по умолчанию значение 3).
        :param page: Номер страницы для вывода (должно быть >=1, по умолчанию
            значение 1).
        :param show_all: Выбирать сразу (True) все записи, соответствующие
                запросу, или выполнить ограниченную выборку (False или None).
                Может отсутствовать.
        :param hotels_with_free_rooms: Выбирать отели со свободными номерами
                в указанные даты (True) или выбирать полный список отелей,
                не учитывая указанные даты (False или None).
                Может отсутствовать.
        :param date_from: Дата, С которой бронируется номер.
            Используется, если параметр hotels_with_free_rooms=True.
        :param date_to: Дата, ДО которой бронируется номер.
            Используется, если параметр hotels_with_free_rooms=True.
        :param filter_by: Фильтры для запроса - конструкция .filter_by(**filter_by).
        :return: Возвращает список:
            [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
             HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
             ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
            Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema

        Если элементы, соответствующие запросу на редактирование в параметре edit_stmt
        и фильтрам, указанным в **filtering, отсутствуют, возбуждается исключение
        HTTPException с кодом 404.
        """

        if query is None:
            query = sa_select(self.model)

        if hotels_with_free_rooms:
            # Выбирать отели со свободными номерами в указанные даты (True)
            if date_from and date_to:
                query = query.filter(await self.get_filtered_by_time(date_from=date_from,
                                                                     date_to=date_to))
            else:
                # status_code=422: Запрос сформирован правильно, но его невозможно
                #                  выполнить из-за семантических ошибок
                #                  Unprocessable Content (WebDAV)
                raise HTTPException(status_code=422,
                                    detail={"description": "Не заданы даты для выбора "
                                                           "отелей со свободными номерами",
                                            })
        if title:
            query = query.filter(sa_func.lower(self.model.title)
                                 .contains(title.strip().lower()))
        if location:
            query = query.filter(sa_func.lower(self.model.location)
                                 .contains(location.strip().lower()))
        result = await super().get_rows(*filter,
                                        query=query,
                                        per_page=per_page,
                                        page=page,
                                        show_all=show_all,
                                        **filter_by
                                        )
        # Возвращает пустой список: [] или список:
        # [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
        #  HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
        #  ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        if len(result) == 0:
            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            raise HTTPException(status_code=404,
                                detail={"description": "Данные отсутствуют.",
                                        })
        if show_all:
            status = "Полный список отелей."
        else:
            status = (f'Страница {page}, установлено отображение '
                      f'{per_page} элемент(-а/-ов) на странице.')

        status = (status,
                  f"Всего выводится {len(result)} элемент(-а/-ов) на странице.")
        return {"status": status, "hotels": result}

    async def get_one_or_none_my_err(self,
                                     query=None,
                                     title=None,
                                     location=None,
                                     **filtering,
                                     ):
        """
        Метод класса. Возвращает одну строку или None. Если получено более
        одной строки, то поднимается исключение MultipleResultsFound.
        Использует родительский метод get_rows.

        :param query: SQL-Запрос. Если простой SELECT-запрос на выборку,
            то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :param title: Наименование отеля.
        :param location: Адрес отеля.
        :param filtering: Значения фильтра для выборки объекта. Используется
            фильтр только на точное равенство: filter_by(**filtering), который
            преобразуется в конструкцию (для примера): WHERE hotels.id = 188

        :return: Возвращает первую строку результата или None если результатов нет,
            или вызывает исключение если есть более одного результата.
            - список, содержащий один элемент, преобразованный к схеме Pydantic (self.schema):
              [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16)]
            - ошибку MultipleResultsFound, если более одного результата.
            - None если результатов нет.
        Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        """
        if query is None:
            query = sa_select(self.model)

        if title:
            query = query.filter(sa_func.lower(self.model.title)
                                 .contains(title.strip().lower()))
        if location:
            query = query.filter(sa_func.lower(self.model.location)
                                 .contains(location.strip().lower()))

        query = query.filter_by(**filtering)

        result = await super().get_rows(query=query, limit=2, offset=0)
        # Возвращает пустой список: [] или список:
        # [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16]
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        # В случае, если возвращается два экземпляра:
        # [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16,
        #  HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17)]
        # то требуется поднять ошибку sqlalchemy.orm.exc.MultipleResultsFound.
        # Так написано в документации:
        # - method sqlalchemy.engine.Result.one_or_none() → Row[_TP] | None¶
        # https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Result.one_or_none
        # -  method sqlalchemy.orm.Query.one_or_none() → _T | None¶
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.one_or_none

        if len(result) > 1:
            raise MultipleResultsFound
        return result if result else None
        # return result.scalars().one_or_none()

    # async def add(self, added_data: BaseModel, **kwargs):
    #     """
    #     Метод класса. Добавляет один объект в базу, используя метод
    #     insert. Служит обёрткой для родительского метода add.
    #
    #     :param added_data: Добавляемые данные.
    #     :param kwargs: Возможные иные именованные аргументы (не используются).
    #
    #     :return: Возвращает список, содержащий добавленный объект.
    #     """
    #     # Теоретически, эта функция не нужна, так как наследуется
    #     # от родителя из класса BaseRepositoryMyCode. Но вставлена
    #     # на случай, если потребуется дополнительная обработка.
    #
    #     result = await super().add(added_data, **kwargs)
    #     return result

    async def edit(self,
                   edited_data: BaseModel,
                   edit_stmt=None,
                   exclude_unset: bool = False,
                   **filtering):  # -> None:
        """
        Метод класса. Редактирует один объект в базе, используя метод
        update. Служит обёрткой для родительского метода edit.

        :param edited_data: Новые значения для внесения в выбранную запись.
        :param edit_stmt: SQL-Запрос на редактирование. Если простой UPDATE-запрос на
            редактирование, то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :param exclude_unset: Редактировать все поля модели (True) или
               редактировать только те поля, которым явно присвоено значением
               (даже если присвоили None).
        :param filtering: Значения фильтра для выборки объекта. Используется
            фильтр только на точное равенство: filter_by(**filtering), который
            преобразуется в конструкцию (для примера): WHERE hotels.id = 188

        :return: Возвращает словарь: {"updated hotels":  list(dict)},
                где:
                - updated_hotels. Список, содержащий отредактированный объект(ы). Выводится
                  в виде списка:
                  [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
                   HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
                   ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
                  Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema

        Если элементы, соответствующие запросу на редактирование в параметре edit_stmt
        и фильтрам, указанным в **filtering, отсутствуют, возбуждается исключение
        HTTPException с кодом 404.
        """
        result = await super().edit(edited_data, edit_stmt, exclude_unset, **filtering)
        if len(result) == 0:
            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            raise HTTPException(status_code=404,
                                detail={"description": "Для отеля с идентификатором "
                                                       f"{filtering['id']} ничего не найдено",
                                        })
        return {"updated hotels": result}

    async def delete(self, delete_stmt=None, **filtering):  # -> None:
        """
        Метод класса. Удаляет объект или объекты в базе, используя метод
        delete. Служит обёрткой для родительского метода delete.

        :param delete_stmt: SQL-Запрос. Если простой SELECT-запрос на выборку,
            то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :param filtering: Значения фильтра для выборки объекта. Используется
            фильтр только на точное равенство: filter_by(**filtering), который
            преобразуется в конструкцию (для примера): WHERE hotels.id = 188

        :return: Возвращает словарь:
            {"deleted hotels": list(dict)},
            где:
            - deleted_hotels: Список с удалёнными элементами:
                  [HotelPydanticSchema(title='title_string_1',
                                       location='location_string_1', id=16),
                   HotelPydanticSchema(title='title_string_2',
                                       location='location_string_2', id=17),
                   ..., HotelPydanticSchema(title='title_string_N',
                                            location='location_string_N', id=198)]
                  Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema

        Если элементы, соответствующие запросу на удаление в параметре delete_stmt
        и фильтрам, указанным в **filtering, отсутствуют, возбуждается исключение
        HTTPException с кодом 404.
        """
        result = await super().delete(delete_stmt, **filtering)
        if len(result) == 0:
            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            raise HTTPException(status_code=404,
                                detail={"description": "Не найден(ы) отель "
                                                       "(отели) для удаления",
                                        })
        return {"deleted hotels": result}

    async def get_id(self, hotel_id: int):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (поле self.model.id) один
        объект в базе, используя метод get. Служит обёрткой для родительского
        метода get_id.

        :param hotel_id: Идентификатор выбираемого объекта.

        :return: Возвращает словарь: {"got hotel": dict},
        где:
        - got_hotel: Выбранный объект. Выводятся в виде словаря элементы
            объекта HotelPydanticSchema:
            HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16).
            Тип возвращаемого элемента преобразован к схеме Pydantic: self.schema

        Если элемент, соответствующий hotel_id отсутствует, возбуждается исключение
        HTTPException с кодом 404.
        """

        # result = await self.session.get(self.model, object_id)
        result = await super().get_id(hotel_id)
        # result: None или <src.models.hotels.HotelsORM object at 0x0000023FB96EAD90>
        # Возвращает пустой список: [] или объект:
        # HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16)
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        if not result:
            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            raise HTTPException(status_code=404,
                                detail={"description": "Для отеля с идентификатором "
                                                       f"{hotel_id} ничего не найдено",
                                        })
        return {"got hotel": result}
