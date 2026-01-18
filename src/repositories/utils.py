from datetime import date

from sqlalchemy import select, func, insert

from src.models.bookings import BookingsORM
from src.models.rooms import RoomsORM


def rooms_ids_for_booking_query(date_from: date,
                                date_to: date,
                                hotel_id: int | None = None):
    # Делаем такой запрос:
    # --ЗАЕЗД '2025-01-20'
    # --ВЫЕЗД '2025-01-23'
    # -- date_from д.б. <= даты ВЫЕЗДА - это дата, С которой бронируется номер
    # -- date_to д.б. <= даты ЗАЕЗДА - это дата, ДО которой бронируется номер
    #
    # Оператор WITH в MySQL служит для создания временного общего табличного
    # выражения (Common Table Expression, CTE), которое можно затем включить
    # в SQL-запрос.
    #
    # with rooms_count as (
    # 	--Получаем количество брони в период с date_from до date_to
    #   --То есть, это ЗАНЯТЫЕ номера
    # 	--Выводятся столбцы: room_id и rooms_booked
    # 	select room_id, count(*) as rooms_booked from bookings
    # 	where date_from <= '2025-01-24' and date_to >= '2025-01-20'
    # 	group by room_id
    # ),
    # rooms_left_table as (
    # 	--Получаем количество свободных номеров.
    # 	--Выводятся столбцы: room_id и rooms_left
    # 	--rooms_left может иметь значения >= 0.
    # 	select rooms.id as room_id, quantity - coalesce(rooms_booked, 0) as rooms_left
    # 	from rooms
    # 	left join rooms_count on rooms.id = rooms_count.room_id
    # )
    # --Выбираем значения, в которых rooms_left > 0 - то есть, положительное, не равное нулю
    # select * from rooms_left_table
    # where rooms_left > 0;

    # Запрос разбит на ТРИ части.

    # Часть 1:
    # with rooms_count as (
    # 	--Получаем количество брони в период с date_from до date_to
    #   --То есть, это ЗАНЯТЫЕ номера
    # 	--Выводятся столбцы: room_id и rooms_booked
    # 	select room_id, count(*) as rooms_booked from bookings
    # 	where date_from <= '2025-01-24' and date_to >= '2025-01-20'
    # 	group by room_id
    # ),
    rooms_count = (select(BookingsORM.room_id,
                          func.count("*").label("rooms_booked"))
                   .select_from(BookingsORM)
                   .filter(BookingsORM.date_from <= date_to,
                           BookingsORM.date_to >= date_from)
                   .group_by(BookingsORM.room_id)
                   .cte(name="rooms_count"))
    # cte - это чтоб алхимия могла сформировать большой запрос

    # Часть 2:
    # rooms_left_table as (
    # 	--Получаем количество свободных номеров.
    # 	--Выводятся столбцы: room_id и rooms_left
    # 	--rooms_left может иметь значения >= 0.
    # 	select rooms.id as room_id, quantity - coalesce(rooms_booked, 0) as rooms_left
    # 	from rooms
    # 	left join rooms_count on rooms.id = rooms_count.room_id
    # )
    rooms_left_table = (select(RoomsORM.id.label("room_id"),
                               (RoomsORM.quantity -
                                func.coalesce(rooms_count.c.rooms_booked, 0)).label("rooms_left"))
                        .select_from(RoomsORM)
                        .outerjoin(rooms_count, RoomsORM.id == rooms_count.c.room_id)
                        .cte(name="rooms_left_table"))
    # Так как rooms_count - это объект CTE, а не алхимии,
    # то к столбцам/колонкам надо обращаться через параметр ".c".
    # Колонки в rooms_count: room_id и rooms_booked.
    # .outerjoin - это аналог left join в SQL. В алхимии right join
    # отсутствует, и чтоб его сделать, надо поменять таблицы местами.

    # Часть 3:
    # --Выбираем значения, в которых rooms_left > 0 - то есть, положительное, не равное нулю
    # select * from rooms_left_table
    # where rooms_left > 0;
    # query = (select(rooms_left_table)  # Выбираем все столбцы из таблицы
    #          .select_from(rooms_left_table)
    #          .filter(rooms_left_table.c.rooms_left > 0))
    # Выводим полученный запрос
    # print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))
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
    # SELECT rooms_left_table.room_id,
    #        rooms_left_table.rooms_left
    # FROM rooms_left_table
    # WHERE rooms_left_table.rooms_left > 0

    # Так как нам надо ещё выбирать и для конкретного отеля, то в последней выборке
    # добавляем условие на выбор номеров, соответствующих указанному hotel_id:
    # Поэтому последний запрос надо сделать таким:
    # --Выбираем значения, в которых rooms_left > 0 - то есть, положительное,
    # -- не равное нулю, и номера относятся к указанному отелю.
    # select * from rooms_left_table
    # where rooms_left > 0 and room_id in (select id from rooms where hotel_id = 176);

    # оформляем отдельным выражением подзапрос:
    # select id from rooms where hotel_id = 176
    # где вместо 176 указываем параметр hotel_id

    # Так выглядит полный запрос:
    # rooms_ids_for_hotel = (select(RoomsORM.id)
    #                        .select_from(RoomsORM)
    #                        .filter_by(hotel_id=hotel_id)
    #                        .subquery(name="rooms_ids_for_hotel"))

    # Но надо проверить, что если hotel_id = None, то тогда
    # исключить конструкцию filter_by(hotel_id=hotel_id).
    # Это на случай, если надо искать свободные номера по
    # всем отелям, а не только по указанному отелю.
    rooms_ids_for_hotel = (select(RoomsORM.id)
                           .select_from(RoomsORM)
                           )

    if hotel_id is not None:
        rooms_ids_for_hotel = (rooms_ids_for_hotel
                               .filter_by(hotel_id=hotel_id)
                               )

    rooms_ids_for_hotel = (rooms_ids_for_hotel
                           .subquery(name="rooms_ids_for_hotel")
                           )

    # если в subquery не указать name="rooms_ids_for_hotel", то тогда будет
    # использоваться конструкция с anon_1:
    # SELECT anon_1.id
    # FROM (SELECT rooms.id AS id
    #       FROM rooms
    #       WHERE rooms.hotel_id = 176) AS anon_1
    # Если указать .subquery(name="rooms_ids_for_hotel"), то получим более читаемое:
    # SELECT rooms_ids_for_hotel.id
    # FROM (SELECT rooms.id AS id
    #       FROM rooms
    #       WHERE rooms.hotel_id = 176) AS rooms_ids_for_hotel

    # общий запрос выглядит так:
    # query = (select(rooms_left_table)  # Выбираем все столбцы из таблицы
    #          .select_from(rooms_left_table)
    #          .filter(rooms_left_table.c.rooms_left > 0,
    #                  rooms_left_table.c.room_id.in_(rooms_ids_for_hotel),
    #                  )
    #          )

    # можно дополнительно добавить условие в ранее сделанный запрос
    # query = (query.filter(rooms_left_table.c.room_id.in_(rooms_ids_for_hotel)
    #                       )
    #          )
    # Выводим полученный запрос
    # print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))

    # Выбираем только идентификаторы номеров
    rooms_ids_to_get = (select(rooms_left_table.c.room_id)  # Выбираем столбец room_id
                        .select_from(rooms_left_table)
                        .filter(rooms_left_table.c.rooms_left > 0,
                                rooms_left_table.c.room_id.in_(rooms_ids_for_hotel),
                                )
                        )
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
    #
    # То есть, в последнем SELECT ранее выбиралось два поля (room_id и rooms_left):
    # SELECT rooms_left_table.room_id,
    #        rooms_left_table.rooms_left
    # FROM rooms_left_table
    # а теперь только одно: rooms_left_table.room_id

    return rooms_ids_to_get