from datetime import date
from typing import Union, Callable

from fastapi import HTTPException
from pydantic import BaseModel

from sqlalchemy import func as sa_func, and_

from sqlalchemy import select as sa_select  # Для реализации SQL команды SELECT
from sqlalchemy import delete as sa_delete  # Для реализации SQL команды DELETE
from sqlalchemy import update as sa_update  # Для реализации SQL команды UPDATE
from sqlalchemy import insert as sa_insert  # Для реализации SQL команды INSERT

from sqlalchemy import Select as sa_Select  # Тип функции sa_select
from sqlalchemy import Delete as sa_Delete  # Тип функции sa_delete
from sqlalchemy import Update as sa_Update  # Тип функции sa_update
from sqlalchemy import Insert as sa_Insert  # Тип функции sa_insert

from sqlalchemy.exc import IntegrityError

from src.repositories.base import BaseRepository

from src.models.rooms import RoomsORM
from src.repositories.hotels import HotelsRepository
from src.repositories.utils import rooms_ids_for_booking_query
from src.schemas.rooms import RoomPydanticSchema

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
# или с явным указанием имени параметра:
# print(add_stmt.compile(bind=engine, compile_kwargs={"literal_binds": True}))
# # Вывод: INSERT INTO hotels (title, location)
# #        VALUES ('title_string', 'location_string')
# #        RETURNING hotels.id


class RoomsRepository(BaseRepository):
    model = RoomsORM
    schema = RoomPydanticSchema

    # Надо сделать обработку URL:
    # 1. Вывести информацию по всем номерам отеля
    # 2. Выбрать инфо по конкретному номеру по id
    # 3. Добавить номер с примерами данных
    # 4. Изменять номер post
    # 5. Изменять номер patch
    # 6. Удалять номер

    # Сделаны методы:
    #
    # - check_hotel_id. Проверяем, существует ли отель с указанным id=hotel_id.
    # - create_stmt_for_selection. Формирует запрос для удаления или для
    #       выборки строк, в зависимости от переданного метода sa_select, sa_delete
    # - get_all. Выбирает все строки для указанного отеля.
    #       Использует родительский метод get_rows.
    # - get_filtered_by_time. Выбирает все свободные номера в указанный
    #       промежуток времени (от date_from до date_to) для указанного отеля.
    #       Использует родительский метод get_rows.
    # - get_id. Выбирает по идентификатору (поле self.model.id) один объект
    #       в базе, используя метод get.
    #       Служит обёрткой для родительского метода get_id.
    # - delete. Удаляет объект или объекты в базе, используя метод delete.
    #       Служит обёрткой для родительского метода delete.
    # - delete_id. Выбирает по идентификатору (по первичному ключу) - поле
    #       self.model.id один объект в базе, используя метод get, удаляет
    #       методом session.delete.
    #       Служит обёрткой для родительского метода delete_id.
    # - edit_id. Редактирует один объект в базе, выбирая по идентификатору
    #       (по первичному ключу) - поле self.model.id один объект в базе,
    #       используя метод get.
    #       Редактирует один объект в базе, обновление реализовано через обновление
    #       атрибутов объекта: setattr(updated_object, key, value).
    #       Служит обёрткой для родительского метода edit_id.
    # - edit. Редактирует один объект в базе, используя метод update.
    #       Служит обёрткой для родительского метода edit.
    # - add. Добавляет один объект в базе, используя метод insert.
    #       Служит обёрткой для родительского метода add.

    async def check_hotel_id(self,
                             hotel_id: int,
                             room_data: BaseModel | None = None):  # -> None:
        """
        Метод класса. Проверяем, существует ли отель с указанным id=hotel_id.

        :param room_data: Донные о номере, в которых имеется связь
            с таблицей отелей.
        :param hotel_id: Идентификатор отеля для проверки - имеется
            такая запись или нет.

        :return: Ничего не возвращает. В случае, если по hotel_id отсутствует
            запись в таблице отелей, то поднимается исключение HTTPException.
        """

        if hotel_id is None:
            # status_code=422: Запрос сформирован правильно, но его невозможно
            #                  выполнить из-за семантических ошибок
            #                  Unprocessable Content (WebDAV)
            raise HTTPException(status_code=422,
                                detail={"description": "Не задан идентификатор отеля",
                                        })

        # Смотрим по id=hotel_id в модели HotelsRepository.model наличие записи.
        # Возвращает запись или None.
        result = await self.session.get(HotelsRepository.model, hotel_id)

        if result is None:
            detail = {"description": "Отель с идентификатором "
                                     f"{hotel_id} отсутствует"}
            if room_data is not None:
                detail.update({"room_data": room_data.model_dump()})

            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            # raise HTTPException(status_code=404,
            #                     detail={"description": "Отель с указанным идентификатором "
            #                                            f"{hotel_id} отсутствует",
            #                             "room_data": room_data.model_dump()})
            raise HTTPException(status_code=404,
                                detail=detail)

    sql_func_type = Callable[[Union[sa_select, sa_delete, sa_update, sa_insert]
                              ],
                             Union[sa_Select, sa_Delete, sa_Update, sa_Insert]
                             ]

    async def create_stmt_for_selection(self,
                                        title: dict[str | None,
                                                    bool | None,
                                                    bool | None],
                                        description: dict[str | None,
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
                rooms_stmt = select(self.model)
            - sqlalchemy.delete. Исходный запрос формируется:
                rooms_stmt = delete(self.model)

        :param title: Словарь с параметрами для формирования поиска по
            наименованию номера - по полю title.
            Параметр обязательный, словарь должен иметь вид:
            title: {"search_string": str | None = None,
                    "case_sensitivity": bool | None = None,
                    "starts_with": bool | None = None, }
            title["search_string"] - Строка для поиска по наименованию номера
            title["case_sensitivity"] - Поиск с учётом регистра (True) или
                регистронезависимый поиск (False или None). Может отсутствовать
            title["starts_with"] - Поиск строк, начинающихся с заданного
                текста (True), или поиск строк, содержащих заданный текст
                (False или None).

            Если не задано значение для параметра title или не задано значение
            title["search_string"] - поиск по наименованию номера не производится.

        :param description: Словарь с параметрами для формирования поиска по
            Описание номера - по полю description.
            Параметр обязательный, словарь должен иметь вид:
            description: {"search_string": str | None = None,
                          "case_sensitivity": bool | None = None,
                          "starts_with": bool | None = None, }
            description["search_string"] - Строка для поиска по Описание номера
            description["case_sensitivity"] - Поиск с учётом регистра (True) или
                регистронезависимый поиск (False или None). Может отсутствовать
            description["starts_with"] - Поиск строк, начинающихся с заданного
                текста (True), или поиск строк, содержащих заданный текст
                (False или None).

            Если не задано значение для параметра description или не задано значение
            description["search_string"] - поиск по описанию номера не производится.

        :param order_by: Добавить упорядочивание результатов (True) или нет (False или None).


        :return: Возвращает SQL-запрос с добавленными параметрами для поиска по
            адресу и наименованию отеля или SQL-запрос выбирающий все данные.
        """

        if not (description.get("search_string", False)
                or
                title.get("search_string", False)):
            # status_code=422: Запрос сформирован правильно, но его невозможно
            #                  выполнить из-за семантических ошибок
            #                  Unprocessable Content (WebDAV)
            raise HTTPException(status_code=422,
                                detail={"description": "Не заданы параметры для выбора номера",
                                        })

        rooms_stmt = sql_func(self.model)
        # В зависимости от значения sql_func переменная rooms_stmt принимает значения:
        # - sql_func: sa_select
        #   rooms_stmt: SELECT hotels.id, hotels.title, hotels.location
        #                FROM hotels
        # - sql_func: sa_delete
        #   rooms_stmt: DELETE FROM hotels

        # location: {"search_string": None,         # Строка для поиска
        #            "case_sensitivity": None,      # Поиск с учётом регистра (True)
        #            "starts_with": None, }         # Поиск строк, начинающихся с заданного текста (True)
        search_string = description.get("search_string", "")
        if search_string:
            starts_with = '' if description.get("starts_with", False) else '%'
            if description.get("case_sensitivity", False):  # по умолчанию - None
                rooms_stmt = (rooms_stmt
                              .where(self.model.description.like(starts_with + search_string + "%"))
                              )
                print("111111111111111")
                print(rooms_stmt.compile(compile_kwargs={"literal_binds": True}))

                # Параметр sql_func: sa_select
                # rooms_stmt: SELECT hotels.id, hotels.title, hotels.location
                #              FROM hotels
                #              WHERE hotels.location LIKE :location_1
                # или
                # Параметр sql_func: sa_delete
                # rooms_stmt: DELETE FROM hotels WHERE hotels.location LIKE :location_1

            else:
                rooms_stmt = (rooms_stmt
                              .where(self.model.description.ilike(starts_with + search_string + "%"))
                              )
                print("2222222222222222")
                print(rooms_stmt.compile(compile_kwargs={"literal_binds": True}))
                # Параметр sql_func: sa_select
                # rooms_stmt: SELECT hotels.id, hotels.title, hotels.location
                #              FROM hotels
                #              WHERE lower(hotels.location) LIKE lower(:location_1)
                # или
                # Параметр sql_func: sa_delete
                # rooms_stmt: DELETE FROM hotels WHERE lower(hotels.location) LIKE lower(:location_1)

        # title: {"search_string": None,         # Строка для поиска
        #         "case_sensitivity": None,      # Поиск с учётом регистра (True)
        #         "starts_with": None, }         # Поиск строк, начинающихся с заданного текста (True)
        search_string = title.get("search_string", "")
        if search_string:
            starts_with = '' if title.get("starts_with", False) else '%'
            if title.get("case_sensitivity", False):  # по умолчанию - None
                rooms_stmt = (rooms_stmt
                              .where(self.model.title.like(starts_with + search_string + "%"))
                              )
                print("333333333333333")
                print(rooms_stmt.compile(compile_kwargs={"literal_binds": True}))
                # SELECT hotels.id, hotels.title, hotels.location
                # FROM hotels
                # WHERE hotels.title LIKE :title_1
                # или такой запрос (сочетание поиска с учётом регистра может быть разным):
                # SELECT hotels.id, hotels.title, hotels.location
                # FROM hotels
                # WHERE hotels.location LIKE :location_1 AND hotels.title LIKE :title_1
            else:
                rooms_stmt = (rooms_stmt
                              .where(self.model.title.ilike(starts_with + search_string + "%"))
                              )
                print("44444444444444")
                print(rooms_stmt.compile(compile_kwargs={"literal_binds": True}))
                # SELECT hotels.id, hotels.title, hotels.location
                # FROM hotels
                # WHERE lower(hotels.title) LIKE lower(:title_1)
                # или такой запрос (сочетание поиска с учётом регистра может быть разным):
                # SELECT hotels.id, hotels.title, hotels.location
                # FROM hotels
                # WHERE lower(hotels.location) LIKE lower(:location_1) AND lower(hotels.title) LIKE lower(:title_1)

        if order_by:
            rooms_stmt = rooms_stmt.order_by(self.model.id)
            print("555555555555555")
            print(rooms_stmt.compile(compile_kwargs={"literal_binds": True}))

        print("Итоговый запрос:\n", rooms_stmt.compile(compile_kwargs={"literal_binds": True}))

        return rooms_stmt

    async def get_filtered_by_time(self,
                                   hotel_id: int,
                                   date_from: date,
                                   date_to: date):
        """
        Метод класса. Выбирает все свободные номера в указанный промежуток времени
        (от date_from до date_to) для указанного отеля.
        Использует родительский метод get_rows.

        :return: Возвращает пустой список: [] или список из выбранных строк:
                [RoomPydanticSchema(hotel_id=176,
                                    title='title_string_1',
                                    description='description_string_1',
                                    price=214, quantity=5, id=14),
                 RoomPydanticSchema(hotel_id=17,
                                    title='title_string_2',
                                    description='description_string_2',
                                    price=7152, quantity=4, id=15)],
                 ..., RoomPydanticSchema(hotel_id=17,
                                    title='title_string_2',
                                    description='description_string_2',
                                    price=7152, quantity=4, id=15)]
                Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        """

        # --ЗАЕЗД '2025-01-20'
        # --ВЫЕЗД '2025-01-23'
        # -- date_from д.б. <= даты ВЫЕЗДА - это дата, С которой бронируется номер
        # -- date_to д.б. <= даты ЗАЕЗДА - это дата, ДО которой бронируется номер
        #
        # Делаем такой запрос:
        # WITH rooms_count AS (
        #         --Получаем количество брони в период с date_from до date_to
        #         --То есть, это ЗАНЯТЫЕ номера
        #         --Выводятся столбцы: room_id и rooms_booked
        #         SELECT bookings.room_id AS room_id,
        #                count('*') AS rooms_booked
        #         FROM bookings
        #         WHERE bookings.date_from <= '2025-01-23' AND
        #               bookings.date_to >= '2025-01-20'
        #         GROUP BY bookings.room_id
        # ),
        #     rooms_left_table AS (
        #         --Получаем количество свободных номеров.
        #         --Выводятся столбцы: room_id и rooms_left
        #         --rooms_left может иметь значения >= 0.
        #         SELECT rooms.id AS room_id,
        #                rooms.quantity - coalesce(rooms_count.rooms_booked, 0) AS rooms_left
        #         FROM rooms
        #         LEFT OUTER JOIN rooms_count ON rooms.id = rooms_count.room_id
        # )
        # --Выбираем значения, в которых rooms_left > 0 - то есть, положительное, не равное нулю
        # SELECT rooms_left_table.room_id
        # FROM rooms_left_table
        # WHERE rooms_left_table.rooms_left > 0 AND
        #       --Добавляем условие на выбор номеров, соответствующих указанному hotel_id
        #       --(там, где стоит 176) - это если надо выбирать по конкретному отелю.
        #       rooms_left_table.room_id IN (SELECT rooms_ids_for_hotel.id
        #                                    FROM (SELECT rooms.id AS id
        #                                          FROM rooms
        #                                          WHERE rooms.hotel_id = 176) AS rooms_ids_for_hotel)
        rooms_ids_to_get = rooms_ids_for_booking_query(date_from=date_from,
                                                       date_to=date_to,
                                                       hotel_id=hotel_id)
        # print(rooms_ids_to_get.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        # Итоговый запрос:
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
        # SELECT rooms_left_table.room_id
        # FROM rooms_left_table
        # WHERE rooms_left_table.rooms_left > 0 AND
        #       rooms_left_table.room_id IN (SELECT rooms_ids_for_hotel.id
        #                                    FROM (SELECT rooms.id AS id
        #                                          FROM rooms
        #                                          WHERE rooms.hotel_id = 176) AS rooms_ids_for_hotel)

        # return await self.get_filtered(RoomsORM.id.in_(rooms_ids_to_get))
        # return await self.get_rows(RoomsORM.id.in_(rooms_ids_to_get), show_all=True)
        return RoomsORM.id.in_(rooms_ids_to_get)

    async def get_all(self, hotel_id):
        """
        Метод класса. Выбирает все строки для указанного отеля.
        Использует родительский метод get_rows.

        :param hotel_id: Идентификатор отеля

        :return: Возвращает пустой список: [] или список из выбранных строк:
        [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
         HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
         ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
        Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        """
        # Если отсутствует в таблице отелей запись с hotels.id=hotel_id, то тогда
        # не будет и в таблице номеров записи, в которой rooms.hotel_id=hotel_id.

        # Для разделения этой ситуации и ситуации, когда по запросу для существующего
        # отеля нет номеров (вообще нет номеров или нет номеров, соответствующих запросу)
        # можно использовать дополнительную проверку на существование отеля с указанным
        # идентификатором hotel_id в таблице отелей, используя self.check_hotel_id().

        # В этом случае сообщения могут быть в зависимости от ситуации такие:
        # 1. Отель с идентификатором 2 отсутствует
        # 2. Для отеля с идентификатором 2 комнаты не найдено

        # Если не использовать self.check_hotel_id(), то сообщение будет только одно:
        # 1. Для отеля с идентификатором 2 комнаты не найдено
        # И не понятно, нет номеров для отеля с таким id, или нет самого отеля с указанным id.

        await self.check_hotel_id(hotel_id=hotel_id)

        # query = sa_select(self.model).filter_by(hotel_id=hotel_id)
        query = (sa_select(self.model).filter_by(hotel_id=hotel_id))
        result = await super().get_rows(query=query,
                                        show_all=True)
        # Возвращает пустой список: [] или список:
        # [RoomPydanticSchema(hotel_id=16, title='title_string_1',
        #                     description='description_string_1', price=2, quantity=3, id=3),
        #  RoomPydanticSchema(hotel_id=16, title='title_string_2',
        #                     description='description_string_2', price=21, quantity=31, id=6)]
        #  ...,
        #  RoomPydanticSchema(hotel_id=16, title='title_string_N',
        #                     description='description_string_N', price=23, quantity=33, id=7)]
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema

        # status = ("Полный список номеров для выбранного отеля.",
        #           f"Всего выводится {len(result)} элемент(-а/-ов) на странице.")
        # return status, ("Данные отсутствуют." if len(result) == 0 else result)

        # status_code=404: Сервер понял запрос, но не нашёл
        #                  соответствующего ресурса по указанному URL
        if len(result) == 0:
            raise HTTPException(status_code=404,
                                detail={"description": "Для отеля с идентификатором "
                                                       f"{hotel_id} комнаты не найдено",
                                        })
        status = ("Полный список номеров для выбранного отеля.",
                  f"Всего выводится {len(result)} элемент(-а/-ов).")
        return {"status": status, "rooms": result}

    async def get_limit(self,
                        *filter,
                        hotel_id: int | None = None,
                        query: sa_Select | None = None,
                        title: str | None = None,
                        description: str | None = None,
                        price_min: int | None = None,
                        price_max: int | None = None,
                        per_page: int | None = None,
                        page: int | None = None,
                        show_all: bool | None = None,
                        free_rooms: bool | None = None,
                        date_from: date | None = None,
                        date_to: date | None = None,
                        **filter_by,
                        ):
        """
        Метод класса. Выбирает заданное количество строк с
        заданным смещением. Использует родительский метод get_rows.

        :param filter: Фильтры для запроса - конструкция .filter(*filter).
        :param hotel_id: Идентификатор отеля
        :param query: SQL-запрос. Если простой SELECT-запрос на выборку,
            то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :param title: Наименование отеля
        :param description: Описание номера
        :param price_min: Минимальная цена номера
        :param price_max: Максимальная цена номера
        :param per_page: Количество элементов на странице (должно быть >=1 и
            <=30, по умолчанию значение 3).
        :param page: Номер страницы для вывода (должно быть >=1, по умолчанию
            значение 1).
        :param show_all: Выбирать сразу (True) все записи, соответствующие
                запросу, или выполнить ограниченную выборку (False или None).
                Может отсутствовать.
        :param free_rooms: Выбирать свободные (не забронированные) номера
                в указанные даты (True) или выбирать полный список номеров,
                не учитывая указанные даты (False или None).
                Может отсутствовать.
        :param date_from: Дата, С которой бронируется номер.
        :param date_to: Дата, ДО которой бронируется номер.
        :param filter_by: Фильтры для запроса - конструкция .filter_by(**filter_by).

        :return: Возвращает список:
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

        Если элементы, соответствующие запросу на редактирование в параметре edit_stmt
        и фильтрам, указанным в **filtering, отсутствуют, возбуждается исключение
        HTTPException с кодом 404.
        """

        # Если отсутствует в таблице отелей запись с hotels.id=hotel_id, то тогда
        # не будет и в таблице номеров записи, в которой rooms.hotel_id=hotel_id.

        # Для разделения этой ситуации и ситуации, когда по запросу для существующего
        # отеля нет номеров (вообще нет номеров или нет номеров, соответствующих запросу)
        # можно использовать дополнительную проверку на существование отеля с указанным
        # идентификатором hotel_id в таблице отелей, используя self.check_hotel_id().

        # В этом случае сообщения могут быть в зависимости от ситуации такие:
        # 1. Отель с идентификатором 2 отсутствует
        # 2. Для отеля с идентификатором 2 комнаты не найдено

        # Если не использовать self.check_hotel_id(), то сообщение будет только одно:
        # 1. Для отеля с идентификатором 2 комнаты не найдено
        # И не понятно, нет номеров для отеля с таким id, или нет самого отеля с указанным id.

        # Возможно, что отслеживание записи с hotels.id=hotel_id будет сделано в передаваемом
        # SQL-запросе. То есть, если query имеет какое-то значение, то в этом случае добавляется
        # фильтр filter_by(hotel_id=hotel_id) только при не пустом значении hotel_id.

        if query is None:
            await self.check_hotel_id(hotel_id=hotel_id)
            query = sa_select(self.model)

        if hotel_id is not None:
            # Возможно, что query будет передаваться через
            # параметры, тогда hotel_id может быть не задано.
            query = query.filter_by(hotel_id=hotel_id)

        if free_rooms:
            # Выбирать свободные (не забронированные) номера в указанные даты (True)
            if date_from and date_to:
                query = query.filter(await self.get_filtered_by_time(hotel_id=hotel_id,
                                                                     date_from=date_from,
                                                                     date_to=date_to))
            else:
                # status_code=422: Запрос сформирован правильно, но его невозможно
                #                  выполнить из-за семантических ошибок
                #                  Unprocessable Content (WebDAV)
                raise HTTPException(status_code=422,
                                    detail={"description": "Не заданы даты для выбора "
                                                           "свободных (не забронированных) номеров",
                                            })
        if title:
            query = query.filter(sa_func.lower(self.model.title)
                                 .contains(title.strip().lower()))
        if description:
            query = query.filter(sa_func.lower(self.model.description)
                                 .contains(description.strip().lower()))

        # According to docs (https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#the-where-clause),
        # Select.where() (https://docs.sqlalchemy.org/en/20/core/selectable.html#sqlalchemy.sql.expression.Select.where)
        # also accepts multiple conditions as *whereclause with default AND behavior:
        # .where(and_(self.model.price >= price_min, self.model.price <= price_max))
        # .where(self.model.price >= price_min, self.model.price <= price_max)
        # .where(self.model.price >= price_min).where(self.model.price <= price_max)
        # преобразуется в команду SQL:
        # WHERE rooms.price >= price_min AND rooms.user_id <= price_max
        if price_min:
            query = query.where(self.model.price >= price_min)

        if price_max:
            query = query.where(self.model.price <= price_max)

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
            status = "Полный список номеров."
        else:
            status = (f'Страница {page}, установлено отображение '
                      f'{per_page} элемент(-а/-ов) на странице.')

        status = (status,
                  f"Всего выводится {len(result)} элемент(-а/-ов) на странице.")
        return {"status": status, "rooms": result}

    async def get_id(self, room_id: int):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (поле self.model.id) один
        объект в базе, используя метод get. Служит обёрткой для родительского
        метода get_id.

        :param room_id: Идентификатор выбираемого объекта.

        :return: Возвращает словарь: {"room": dict},
        где:
        - room: Выбранный объект.
            Тип возвращаемого элемента преобразован к схеме Pydantic: self.schema.

        """
        # result = await self.session.get(self.model, object_id)
        result = await super().get_id(room_id)
        # result: None или <src.models.hotels.HotelsORM object at 0x0000023FB96EAD90>
        # Возвращает пустой список: [] или объект:
        # HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16)
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        if not result:
            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            raise HTTPException(status_code=404,
                                detail={"description": "Для комнаты с идентификатором "
                                                       f"{room_id} ничего не найдено",
                                        })
        return {"room": result}

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
            {"deleted rooms": list(dict)},
            где:
            - deleted_rooms: Список с удалёнными элементами:
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
        """
        result = await super().delete(delete_stmt, **filtering)
        if len(result) == 0:
            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            raise HTTPException(status_code=404,
                                detail={"description": "Не найден(ы) номер(а) для удаления",
                                        })
        return {"deleted rooms": result}

    async def delete_id(self, room_id: int):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (по первичному ключу) -
        поле self.model.id один объект в базе, используя метод get, удаляет
        методом session.delete.
        Используются методы:
        - session.get(RoomsORM, id) для получения объекта по ключу
        - session.delete(room_object) для удаления объекта room_object.
        Служит обёрткой для родительского метода delete.

        :param room_id: Идентификатор выбираемого объекта.
        :return: Возвращает None или удалённый объект, преобразованный к схеме
            Pydantic: self.schema.
            Возвращает словарь: {"deleted rooms": deleted_rooms},
            где:
            - deleted_rooms: list(dict | []) - Список, содержащий
              удалённый объект. Выводится в виде списка, содержащего
              элементы объекта HotelsORM. Если не найдены объекты
              для удаления, выводится None (null).
        """
        result = await super().delete_id(object_id=room_id)
        if result is None:
            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            raise HTTPException(status_code=404,
                                detail={"description": "Не найден номер с "
                                                       f"идентификатором {room_id}",
                                        })
        # Другой вариант:
        # result = await super().delete_id(object_id=room_id)
        # if len(result) == 0:
        #     status = f"Для номера с идентификатором {room_id} ничего не найдено"
        #     err_type = 1
        #     return {"status": status, "err_type": err_type, "deleted rows": None}
        return {"deleted rooms": result}

    async def edit_id(self,
                      edited_data: BaseModel,
                      room_id=None,
                      exclude_unset: bool = False
                      ):  # -> None:
        """
        Метод класса. Редактирует один объект в базе, выбирая по
        идентификатору (по первичному ключу) - поле self.model.id
        один объект в базе, используя метод get.
        Служит обёрткой для родительского метода edit.

        :param edited_data: Новые значения для внесения в выбранную запись.
        :param room_id: Идентификатор выбираемого объекта.
        :param exclude_unset: Редактировать все поля модели (True) или
            редактировать только те поля, которым явно присвоено значением
            (даже если присвоили None).

        :return: Возвращает None или отредактированный объект, преобразованный к
            схеме Pydantic: self.schema.
            Возвращает словарь:
                {"updated rooms": updated_rooms},
                где:
                - updated_rooms. Список, содержащий отредактированный объект. Выводится
                  в виде списка, содержащего элементы объекта HotelsORM.
        """
        # Если не сделать проверку на правильность hotel_id, то при выполнении оператора
        # await session.commit() возникнет ошибка:
        # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError)
        #       <class 'asyncpg.exceptions.ForeignKeyViolationError'>: INSERT или UPDATE в
        #       таблице "rooms" нарушает ограничение внешнего ключа "rooms_hotel_id_fkey"
        # DETAIL:  Ключ (hotel_id)=(1768) отсутствует в таблице "hotels".
        # [SQL: UPDATE rooms SET hotel_id=$1::INTEGER, title=$2::VARCHAR,
        #              description=$3::VARCHAR, price=$4::INTEGER
        #       WHERE rooms.id = $5::INTEGER]
        # [parameters: (1768, 'Название номера', 'Описание номера', 2, 12)]
        # (Background on this error at: https://sqlalche.me/e/20/gkpj)

        # Если же нет каких-либо

        await self.check_hotel_id(room_data=edited_data, hotel_id=edited_data.hotel_id)

        result = await super().edit_id(edited_data=edited_data,
                                       object_id=room_id,
                                       exclude_unset=exclude_unset)
        if result is None:
            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            raise HTTPException(status_code=404,
                                detail={"description": "Не найден номер с "
                                                       f"идентификатором {room_id}",
                                        })
        # Другой вариант:
        # result = await super().edit(edited_data=edited_data,
        #                             id=room_id,
        #                             exclude_unset=exclude_unset)
        # if len(result) == 0:
        #     status = f"Для номера с идентификатором {room_id} ничего не найдено"
        #     err_type = 1
        #     return {"status": status, "err_type": err_type, "updated rows": None}
        return {"updated rooms": result}

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

        :return: Возвращает пустой список: [] или список из выбранных строк, тип
            возвращаемых элементов преобразован к схеме Pydantic: self.schema.
            Возвращаемый список содержит отредактированные элементы.
            Возвращает словарь:
                {"updated rooms": updated_rooms},
                где:
                - updated_rooms. Список, содержащий отредактированный объект. Выводится
                  в виде списка, содержащего элементы объекта HotelsORM.
        """
        # Проверяем, имеется ли отель по edited_data.hotel_id
        await self.check_hotel_id(room_data=edited_data, hotel_id=edited_data.hotel_id)

        try:
            # Если нет отеля по идентификатору, указанному в hotel_id, то возникает такая ошибка:
            # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError)
            #       <class 'asyncpg.exceptions.ForeignKeyViolationError'>: INSERT или UPDATE в
            #       таблице "rooms" нарушает ограничение внешнего ключа "rooms_hotel_id_fkey"
            # DETAIL:  Ключ (hotel_id)=(1) отсутствует в таблице "hotels".
            # [SQL: UPDATE rooms SET hotel_id=$1::INTEGER, title=$2::VARCHAR,
            #                        description=$3::VARCHAR, price=$4::INTEGER,
            #                        quantity=$5::INTEGER
            #       WHERE rooms.id = $6::INTEGER
            #       RETURNING rooms.id, rooms.hotel_id, rooms.title,
            #                 rooms.description, rooms.price, rooms.quantity]
            # [parameters: (1, 'Название номера - put', 'Описание номера - put', 2, 3, 12)]
            result = await super().edit(edited_data,
                                        edit_stmt,
                                        exclude_unset,
                                        **filtering)
        except IntegrityError:
            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            raise HTTPException(status_code=404,
                                detail={"description": "Отель с указанным идентификатором "
                                                       f"{edited_data.hotel_id} отсутствует",
                                        "edited_data": edited_data.model_dump()})

        if len(result) == 0:
            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            raise HTTPException(status_code=404,
                                detail={"description": "Не найден номер с "
                                                       f"идентификатором {filtering['id']}",
                                        })
        return {"updated rooms": result}

    async def add(self,
                  added_data: BaseModel,
                  exclude_unset: bool = False):  # -> None:
        """
        Метод класса. Добавляет один объект в базе, используя метод
        insert. Служит обёрткой для родительского метода add.

        :param added_data: Новые значения для внесения в выбранную запись.
        :param exclude_unset: Редактировать все поля модели (True) или
               редактировать только те поля, которым явно присвоено значением
               (даже если присвоили None).

        :return: Возвращает словарь:
                {"added rows": added_rooms},
                где:
                - added_rooms. Список, содержащий отредактированный объект. Выводится
                  в виде списка, содержащего элементы объекта HotelsORM.
        """
        await self.check_hotel_id(room_data=added_data, hotel_id=added_data.hotel_id)

        # Integrity Error - Ошибка целостности

        # Если отель по added_data.hotel_id отсутствует в таблице отелей, то при
        # добавлении такой записи возникает ошибка:
        # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError)
        #       <class 'asyncpg.exceptions.ForeignKeyViolationError'>: INSERT или UPDATE в таблице
        #       "rooms" нарушает ограничение внешнего ключа "rooms_hotel_id_fkey"
        # DETAIL:  Ключ (hotel_id)=(14) отсутствует в таблице "hotels".
        # [SQL: INSERT INTO rooms (hotel_id, title, description, price, quantity)
        #   VALUES ($1::INTEGER, $2::VARCHAR, $3::VARCHAR, $4::INTEGER, $5::INTEGER)
        #   RETURNING rooms.id, rooms.hotel_id, rooms.title,
        #             rooms.description, rooms.price, rooms.quantity]
        # [parameters: (14, 'Название обычного номера', 'Описание обычного номера', 11, 12)]
        # (Background on this error at: https://sqlalche.me/e/20/gkpj)

        # Если не указаны данные для поля, являющегося обязательным (в примере
        # искусственно в поле title установлено значение None), то возникает ошибка:
        # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError)
        #       <class 'asyncpg.exceptions.NotNullViolationError'>: значение NULL в столбце
        #       "title" отношения "rooms" нарушает ограничение NOT NULL
        # DETAIL:  Ошибочная строка содержит (23, 198, null, 198Описание обычного номера, 19811, 19812).
        # [SQL: INSERT INTO rooms (hotel_id, title, description, price, quantity)
        #   VALUES ($1::INTEGER, $2::VARCHAR, $3::VARCHAR, $4::INTEGER, $5::INTEGER)
        #   RETURNING rooms.id, rooms.hotel_id, rooms.title,
        #             rooms.description, rooms.price, rooms.quantity]
        # [parameters: (198, None, '198Описание обычного номера', 19811, 19812)]
        # (Background on this error at: https://sqlalche.me/e/20/gkpj)

        result = await super().add(added_data)
        return {"added rooms": result}

