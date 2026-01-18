from datetime import date
from typing import Union

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func, insert
from sqlalchemy.exc import IntegrityError

from src.database import engine
from src.models.bookings import BookingsORM
from src.repositories.base import BaseRepository

from src.models.rooms import RoomsORM
from src.repositories.hotels import HotelsRepository
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

        query = select(self.model).filter_by(hotel_id=hotel_id)
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

    async def get_filtered_by_time(self,
                                   hotel_id: int,
                                   date_from: date,
                                   date_to: date):  # -> None:
        """
        Метод класса. Выбирает все свободные номера в указанный промежуток времени
        (от date_from до date_to) для указанного отеля.
        Использует родительский метод get_rows.
        """

        # # Делаем такой запрос:
        # # --ЗАЕЗД '2025-01-20'
        # # --ВЫЕЗД '2025-01-23'
        # # -- date_from д.б. <= даты ВЫЕЗДА - это дата, С которой бронируется номер
        # # -- date_to д.б. <= даты ЗАЕЗДА - это дата, ДО которой бронируется номер
        # #
        # # with rooms_count as (
        # # 	--Получаем количество брони в период с date_from до date_to
        # #   --То есть, это ЗАНЯТЫЕ номера
        # # 	--Выводятся столбцы: room_id и rooms_booked
        # # 	select room_id, count(*) as rooms_booked from bookings
        # # 	where date_from <= '2025-01-24' and date_to >= '2025-01-20'
        # # 	group by room_id
        # # ),
        # # rooms_left_table as (
        # # 	--Получаем количество свободных номеров.
        # # 	--Выводятся столбцы: room_id и rooms_left
        # # 	--rooms_left может иметь значения >= 0.
        # # 	select rooms.id as room_id, quantity - coalesce(rooms_booked, 0) as rooms_left
        # # 	from rooms
        # # 	left join rooms_count on rooms.id = rooms_count.room_id
        # # )
        # # --Выбираем значения, в которых rooms_left > 0 - то есть, положительное, не равное нулю
        # # select * from rooms_left_table
        # # where rooms_left > 0;
        #
        # # Запрос разбит на ТРИ части.
        #
        # # Часть 1:
        # # with rooms_count as (
        # # 	--Получаем количество брони в период с date_from до date_to
        # #   --То есть, это ЗАНЯТЫЕ номера
        # # 	--Выводятся столбцы: room_id и rooms_booked
        # # 	select room_id, count(*) as rooms_booked from bookings
        # # 	where date_from <= '2025-01-24' and date_to >= '2025-01-20'
        # # 	group by room_id
        # # ),
        # rooms_count = (select(BookingsORM.room_id,
        #                       func.count("*").label("rooms_booked"))
        #                .select_from(BookingsORM)
        #                .filter(BookingsORM.date_from <= date_to,
        #                        BookingsORM.date_to >= date_from)
        #                .group_by(BookingsORM.room_id)
        #                .cte(name="rooms_count"))
        # # cte - это чтоб алхимия могла сформировать большой запрос
        #
        # # Часть 2:
        # # rooms_left_table as (
        # # 	--Получаем количество свободных номеров.
        # # 	--Выводятся столбцы: room_id и rooms_left
        # # 	--rooms_left может иметь значения >= 0.
        # # 	select rooms.id as room_id, quantity - coalesce(rooms_booked, 0) as rooms_left
        # # 	from rooms
        # # 	left join rooms_count on rooms.id = rooms_count.room_id
        # # )
        # rooms_left_table = (select(RoomsORM.id.label("room_id"),
        #                            (RoomsORM.quantity -
        #                             func.coalesce(rooms_count.c.rooms_booked, 0)).label("rooms_left"))
        #                     .select_from(RoomsORM)
        #                     .outerjoin(rooms_count, RoomsORM.id == rooms_count.c.room_id)
        #                     .cte(name="rooms_left_table"))
        # # Так как rooms_count - это объект CTE, а не алхимии,
        # # то к столбцам/колонкам надо обращаться через параметр ".c".
        # # Колонки в rooms_count: room_id и rooms_booked.
        # # .outerjoin - это аналог left join в SQL. В алхимии right join
        # # отсутствует, и чтоб его сделать, надо поменять таблицы местами.
        #
        # # Часть 3:
        # # --Выбираем значения, в которых rooms_left > 0 - то есть, положительное, не равное нулю
        # # select * from rooms_left_table
        # # where rooms_left > 0;
        # query = (select(rooms_left_table)  # Выбираем все столбцы из таблицы
        #          .select_from(rooms_left_table)
        #          .filter(rooms_left_table.c.rooms_left > 0))
        # # Выводим полученный запрос
        # # print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        # # WITH rooms_count AS (
        # #         SELECT bookings.room_id AS room_id,
        # #                count('*') AS rooms_booked
        # #         FROM bookings
        # #         WHERE bookings.date_from <= '2025-01-23' AND
        # #               bookings.date_to >= '2025-01-20'
        # #         GROUP BY bookings.room_id
        # # ),
        # #     rooms_left_table AS (
        # #         SELECT rooms.id AS room_id,
        # #                rooms.quantity - coalesce(rooms_count.rooms_booked, 0) AS rooms_left
        # #         FROM rooms
        # #         LEFT OUTER JOIN rooms_count ON rooms.id = rooms_count.room_id
        # # )
        # # SELECT rooms_left_table.room_id,
        # #        rooms_left_table.rooms_left
        # # FROM rooms_left_table
        # # WHERE rooms_left_table.rooms_left > 0
        #
        # # Так как нам надо ещё выбирать и для конкретного отеля, то в последней выборке
        # # добавляем условие на выбор номеров, соответствующих указанному hotel_id:
        # # Поэтому последний запрос надо сделать таким:
        # # --Выбираем значения, в которых rooms_left > 0 - то есть, положительное,
        # # -- не равное нулю, и номера относятся к указанному отелю.
        # # select * from rooms_left_table
        # # where rooms_left > 0 and room_id in (select id from rooms where hotel_id = 176);
        #
        # # оформляем отдельным выражением подзапрос:
        # # select id from rooms where hotel_id = 176
        # # где вместо 176 указываем параметр hotel_id
        # rooms_ids_for_hotel = (select(RoomsORM.id)
        #                        .select_from(RoomsORM)
        #                        .filter_by(hotel_id=hotel_id)
        #                        .subquery(name="rooms_ids_for_hotel"))
        # # если в subquery не указать name="rooms_ids_for_hotel", то тогда будет
        # # использоваться конструкция с anon_1:
        # # SELECT anon_1.id
        # # FROM (SELECT rooms.id AS id
        # #       FROM rooms
        # #       WHERE rooms.hotel_id = 176) AS anon_1
        # # Если указать, .subquery(name="rooms_ids_for_hotel"), то получим более читаемое:
        # # SELECT rooms_ids_for_hotel.id
        # # FROM (SELECT rooms.id AS id
        # #       FROM rooms
        # #       WHERE rooms.hotel_id = 176) AS rooms_ids_for_hotel
        #
        # # общий запрос выглядит так:
        # # query = (select(rooms_left_table)  # Выбираем все столбцы из таблицы
        # #          .select_from(rooms_left_table)
        # #          .filter(rooms_left_table.c.rooms_left > 0,
        # #                  rooms_left_table.c.room_id.in_(rooms_ids_for_hotel),
        # #                  )
        # #          )
        #
        # # можно дополнительно добавить условие в ранее сделанный запрос
        # # query = (query.filter(rooms_left_table.c.room_id.in_(rooms_ids_for_hotel)
        # #                       )
        # #          )
        # # Выводим полученный запрос
        # # print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        #
        # # Выбираем только идентификаторы номеров
        # rooms_ids_to_get = (select(rooms_left_table.c.room_id)  # Выбираем столбец room_id
        #                     .select_from(rooms_left_table)
        #                     .filter(rooms_left_table.c.rooms_left > 0,
        #                             rooms_left_table.c.room_id.in_(rooms_ids_for_hotel),
        #                             )
        #                     )
        # # print(rooms_ids_to_get.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        # # Итоговый запрос:
        # # WITH rooms_count AS (
        # #         SELECT bookings.room_id AS room_id,
        # #                count('*') AS rooms_booked
        # #         FROM bookings
        # #         WHERE bookings.date_from <= '2025-01-23' AND
        # #               bookings.date_to >= '2025-01-20'
        # #         GROUP BY bookings.room_id
        # # ),
        # #     rooms_left_table AS (
        # #         SELECT rooms.id AS room_id,
        # #                rooms.quantity - coalesce(rooms_count.rooms_booked, 0) AS rooms_left
        # #         FROM rooms
        # #         LEFT OUTER JOIN rooms_count ON rooms.id = rooms_count.room_id
        # # )
        # # SELECT rooms_left_table.room_id
        # # FROM rooms_left_table
        # # WHERE rooms_left_table.rooms_left > 0 AND
        # #       rooms_left_table.room_id IN (SELECT rooms_ids_for_hotel.id
        # #                                    FROM (SELECT rooms.id AS id
        # #                                          FROM rooms
        # #                                          WHERE rooms.hotel_id = 176) AS rooms_ids_for_hotel)
        # #
        # # То есть, в последнем SELECT ранее выбиралось два поля (room_id и rooms_left):
        # # SELECT rooms_left_table.room_id,
        # #        rooms_left_table.rooms_left
        # # FROM rooms_left_table
        # # а теперь только одно: rooms_left_table.room_id

        return await self.get_filtered(RoomsORM.id.in_(rooms_ids_to_get))

    async def get_id(self, room_id: int):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (поле self.model.id) один
        объект в базе, используя метод get. Служит обёрткой для родительского
        метода get_id.

        :param room_id: Идентификатор выбираемого объекта.

        :return: Возвращает словарь: {"room": dict},
        где:
        - room: Выбранный объект. Выводятся в виде словаря элементы
            объекта HotelsORM.

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
        :return: Возвращает словарь: {"deleted rooms": deleted_rooms},
            где:
            - deleted_rooms: list(dict | []) - Список, содержащий
              удалённый объект. Выводится в виде списка, содержащего
              элементы объекта HotelsORM. Если не найдены объекты
              для удаления, выводится None (null).
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
        :return: Возвращает словарь: {"deleted rooms": deleted_rooms},
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

        :return: Возвращает словарь:
                {"updated rooms": updated_rooms},
                где:
                - updated_rooms. Список, содержащий отредактированный объект. Выводится
                  в виде списка, содержащего элементы объекта HotelsORM.
        """
        # Если не сделать проверку на правильность hotel_id, то при выполнении оператора
        # await session.commit() возникнет ошибка:
        # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: INSERT или UPDATE в таблице "rooms" нарушает ограничение внешнего ключа "rooms_hotel_id_fkey"
        # DETAIL:  Ключ (hotel_id)=(1768) отсутствует в таблице "hotels".
        # [SQL: UPDATE rooms SET hotel_id=$1::INTEGER, title=$2::VARCHAR, description=$3::VARCHAR, price=$4::INTEGER WHERE rooms.id = $5::INTEGER]
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

        :return: Возвращает словарь:
                {"updated rooms": updated_rooms},
                где:
                - updated_rooms. Список, содержащий отредактированный объект. Выводится
                  в виде списка, содержащего элементы объекта HotelsORM.
        """
        # Проверяем, имеется ли отель по edited_data.hotel_id
        await self.check_hotel_id(room_data=edited_data, hotel_id=edited_data.hotel_id)

        try:
            # Если нет отеля по идентификатору, указанному в hotel_id, то возникает такая ошибка:
            # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: INSERT или UPDATE в таблице "rooms" нарушает ограничение внешнего ключа "rooms_hotel_id_fkey"
            # DETAIL:  Ключ (hotel_id)=(1) отсутствует в таблице "hotels".
            # [SQL: UPDATE rooms SET hotel_id=$1::INTEGER, title=$2::VARCHAR, description=$3::VARCHAR, price=$4::INTEGER, quantity=$5::INTEGER WHERE rooms.id = $6::INTEGER RETURNING rooms.id, rooms.hotel_id, rooms.title, rooms.description, rooms.price, rooms.quantity]
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
        # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: INSERT или UPDATE в таблице "rooms" нарушает ограничение внешнего ключа "rooms_hotel_id_fkey"
        # DETAIL:  Ключ (hotel_id)=(14) отсутствует в таблице "hotels".
        # [SQL: INSERT INTO rooms (hotel_id, title, description, price, quantity) VALUES ($1::INTEGER, $2::VARCHAR, $3::VARCHAR, $4::INTEGER, $5::INTEGER) RETURNING rooms.id, rooms.hotel_id, rooms.title, rooms.description, rooms.price, rooms.quantity]
        # [parameters: (14, 'Название обычного номера', 'Описание обычного номера', 11, 12)]
        # (Background on this error at: https://sqlalche.me/e/20/gkpj)

        # Если не указаны данные для поля, являющегося обязательным (в примере
        # искусственно в поле title установлено значение None), то возникает ошибка:
        # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.NotNullViolationError'>: значение NULL в столбце "title" отношения "rooms" нарушает ограничение NOT NULL
        # DETAIL:  Ошибочная строка содержит (23, 198, null, 198Описание обычного номера, 19811, 19812).
        # [SQL: INSERT INTO rooms (hotel_id, title, description, price, quantity) VALUES ($1::INTEGER, $2::VARCHAR, $3::VARCHAR, $4::INTEGER, $5::INTEGER) RETURNING rooms.id, rooms.hotel_id, rooms.title, rooms.description, rooms.price, rooms.quantity]
        # [parameters: (198, None, '198Описание обычного номера', 19811, 19812)]
        # (Background on this error at: https://sqlalche.me/e/20/gkpj)

        result = await super().add(added_data)
        return {"added rooms": result}

