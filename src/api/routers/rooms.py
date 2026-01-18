from fastapi import Body, Path, APIRouter
from typing import Annotated

from src.api.dependencies.dependencies import DBDep

from src.schemas.rooms import RoomPath, HotelRoomPath, HotelPath
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
post("/hotels/room") - Создание записи с новой комнатой в отеле.
        Функция: create_room_post

get("/hotels/{hotel_id}/rooms") - Вывод списка номеров для конкретного 
        отеля - весь список полностью.
        Функция: show_rooms_in_hotel_get

get("/hotels/rooms/{room_id}") - Получение из базы данных выбранной 
        записи по идентификатору отеля.
        Функция: get_rooms_id_get

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

put("/hotels/rooms/{room_id}") - Обновление ВСЕХ данных одновременно 
        для выбранной записи, выборка происходит по идентификатору номера.
        Функция: change_room_put

patch("/hotels/rooms/{room_id}") - Обновление каких-либо данных выборочно 
        или всех данных сразу для выбранной записи, выборка происходит по 
        идентификатору номера.
        Функция: change_room_patch
"""

# Если в списке указывается несколько тегов, то для
# каждого тега создаётся свой раздел в документации
router = APIRouter(prefix="/hotels", tags=["Номера"])


openapi_examples_dict = {"1": {"summary": "Номер обычный (укажите правильное значение для hotel_id)",
                               "value": {"hotel_id": 1,  # int, Идентификатор отеля, в котором находится комната
                                         "title": "Название обычного номера",  # String(length=100)
                                         "description": "Описание обычного номера",  # str
                                         "price": 11,  # int, Цена номера
                                         "quantity": 12,  # int, Общее количество номеров такого типа
                                         }
                               },
                         "2": {"summary": "Люкс (укажите правильное значение для hotel_id)",
                               "value": {"hotel_id": 1,  # int, Идентификатор отеля, в котором находится комната
                                         "title": "Название люкса",  # String(length=100)
                                         "description": "Описание люкса",  # str
                                         "price": 21,  # int, Цена номера
                                         "quantity": 22,  # int, Общее количество номеров такого типа
                                         }
                               }
                         }


@router.post("/room",
             summary="Создание записи с новой комнатой в отеле",
             )
async def create_room_post(room_params: Annotated[RoomDescriptionRecURL,
                                                  Body(openapi_examples=openapi_examples_dict)],
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
    # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.ForeignKeyViolationError'>: INSERT или UPDATE в таблице "rooms" нарушает ограничение внешнего ключа "rooms_hotel_id_fkey"
    # DETAIL:  Ключ (hotel_id)=(1) отсутствует в таблице "hotels".
    # [SQL: INSERT INTO rooms (hotel_id, title, description, price, quantity) VALUES ($1::INTEGER, $2::VARCHAR, $3::VARCHAR, $4::INTEGER, $5::INTEGER) RETURNING rooms.id, rooms.hotel_id, rooms.title, rooms.description, rooms.price, rooms.quantity]
    # [parameters: (1, 'Название номера', 'Описание номера', 2, 3)]
    # (Background on this error at: https://sqlalche.me/e/20/gkpj)

    # Если не указаны данные для поля, являющегося обязательным (в примере
    # искусственно в поле title установлено значение None), то возникает ошибка:
    # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.NotNullViolationError'>: значение NULL в столбце "title" отношения "rooms" нарушает ограничение NOT NULL
    # DETAIL:  Ошибочная строка содержит (23, 198, null, 198Описание обычного номера, 19811, 19812).
    # [SQL: INSERT INTO rooms (hotel_id, title, description, price, quantity) VALUES ($1::INTEGER, $2::VARCHAR, $3::VARCHAR, $4::INTEGER, $5::INTEGER) RETURNING rooms.id, rooms.hotel_id, rooms.title, rooms.description, rooms.price, rooms.quantity]
    # [parameters: (198, None, '198Описание обычного номера', 19811, 19812)]
    # (Background on this error at: https://sqlalche.me/e/20/gkpj)
    result = await db.rooms.add(room_params)
    await db.commit()
    return {"create_room": result}


@router.get("/{hotel_id}/rooms",
            summary="Вывод списка номеров для конкретного отеля - весь список полностью",
            )
# async def show_rooms_in_hotel_get(hotel_id: Path()):
async def show_rooms_in_hotel_get(hotel_path: Annotated[HotelPath, Path()],
                                  db: DBDep):
    return await db.rooms.get_all(hotel_id=hotel_path.hotel_id)


@router.get("/rooms/{room_id}",
            summary="Получение из базы данных выбранной записи по идентификатору отеля",
            )
async def get_rooms_id_get(room: Annotated[RoomPath, Path()], db: DBDep):
    """
    ## Функция получает из базы данных выбранную запись по идентификатору отеля.

    Параметры (передаются в URL):
    - ***:param** room_id:* Идентификатор номера (обязательно).

    ***:return:*** Словарь: `{"status": str, "err_type": int, "got row": dict}`, где:

    - ***status***: Текстовое описание результата операции.;
    - ***err_type***: Код результата операции.
      Принимает значения:
      - 0 (OK: выполнено нормально, без ошибок).
      - 1 (Error: Для объекта с указанным идентификатором ничего не найдено).
      - 2 (Error: Не указан идентификатор отеля для выборки).
    - ***got_row***: Выбранный объект. Выводятся в виде словаря элементы
      объекта HotelsORM.
    """
    result = await db.rooms.get_id(room_id=room.room_id)
    return result


@router.delete("/rooms/{room_id}",
               summary="Удаление выбранной записи по идентификатору номера",
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
               summary="Удаление выбранной записи по идентификатору номера",
               )
# async def delete_hotel_id_del(hotel: Annotated[HotelPath, Path()]):
async def delete_rooms_del(room: Annotated[RoomPath, Path()], db: DBDep):
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

    result = await db.rooms.delete(id=room.room_id)
    await db.commit()  # Подтверждаем изменение
    return result


change_room_examples_lst = [{"hotel_id": 1,  # int, Идентификатор отеля, в котором находится комната
                             "title": "Название номера - put",  # String(length=100)
                             "description": "Описание номера - put",  # str
                             "price": 2,  # int, Цена номера
                             "quantity": 3,  # int, Общее количество номеров такого типа
                             },
                            ]


@router.put("/{hotel_id}/rooms/{room_id}",
            summary="Обновление ВСЕХ данных одновременно для выбранной "
                    "записи, выборка происходит по идентификатору номера",
            )
# async def change_room_hotel_id_put(hotel: Annotated[HotelPath, Path()],
#                                    room: Annotated[RoomPath, Path()],
#                                    room_params: Annotated[RoomDescrRecRequest,
#                                                           Body()],
#                                    ):
async def change_room_hotel_id_put(hotelroom: Annotated[HotelRoomPath, Path()],
                                   room_params: Annotated[RoomDescrRecRequest,
                                                          Body()],
                                   db: DBDep,
                                   ):
    _room_params = RoomDescriptionRecURL(hotel_id=hotelroom.hotel_id,
                                         **room_params.model_dump())

    # result = await db.rooms.edit(edited_data=_room_params,
    #                              id=hotelroom.room_id)
    result = await db.rooms.edit_id(edited_data=_room_params,
                                    room_id=hotelroom.room_id)
    await db.commit()  # Подтверждаем изменение
    # Вариант вместо блока async with async_session_maker() as session:
    # то есть, обращаемся к уже написанной функции change_room_put.
    # Этот вариант может быть хорош, если функция делает какую-то
    # дополнительную обработку.
    # room = RoomPath(room_id=hotelroom.room_id)
    # result = await change_room_put(room=room, room_params=_room_params)
    return result


@router.put("/rooms/{room_id}",
            summary="Обновление ВСЕХ данных одновременно для выбранной "
                    "записи, выборка происходит по идентификатору номера",
            )
async def change_room_put(room: Annotated[RoomPath, Path()],
                          room_params: Annotated[RoomDescriptionRecURL,
                                                 Body(examples=change_room_examples_lst)],
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
    result = await db.rooms.edit(edited_data=room_params,
                                 id=room.room_id)
    # result = await db.rooms.edit_id(edited_data=room_params,
    #                                 room_id=room.room_id)
    await db.commit()  # Подтверждаем изменение
    return result


change_room_examples_lst = [{"hotel_id": 1,  # int, Идентификатор отеля, в котором находится комната
                             "title": "Название номера - patch",  # String(length=100)
                             "description": "Описание номера - patch",  # str
                             "price": 2,  # int, Цена номера
                             "quantity": 3,  # int, Общее количество номеров такого типа
                             },
                            ]


@router.patch("/{hotel_id}/rooms/{room_id}",
              summary="Обновление каких-либо данных выборочно или всех данных сразу "
                      "для выбранной записи, выборка происходит по идентификатору номера",
              )
# async def change_room_hotel_id_patch(room: Annotated[RoomPath, Path(examples=[{"hotel_id": 1}])],
#                                      room_params: Annotated[RoomDescriptionOptURL,
#                                                             Body()],
#                                      ):
async def change_room_hotel_id_patch(hotelroom: Annotated[HotelRoomPath, Path()],
                                     room_params: Annotated[RoomDescrOptRequest,
                                                            Body()],
                                     db: DBDep,
                                     ):
    _room_params = RoomDescriptionOptURL(hotel_id=hotelroom.hotel_id,
                                         **room_params.model_dump(exclude_unset=True))
    # result = await db.rooms.edit(edited_data=_room_params,
    #                              id=hotelroom.room_id,
    #                              exclude_unset=True)
    result = await db.rooms.edit_id(edited_data=_room_params,
                                    room_id=hotelroom.room_id,
                                    exclude_unset=True)
    await db.commit()  # Подтверждаем изменение
    # Вариант вместо блока async with async_session_maker() as session:
    # то есть, обращаемся к уже написанной функции change_room_put.
    # Этот вариант может быть хорош, если функция делает какую-то
    # дополнительную обработку.
    # room = RoomPath(room_id=hotelroom.room_id)
    # result = await change_room_patch(room=room, room_params=_room_params)
    return result


@router.patch("/rooms/{room_id}",
              summary="Обновление каких-либо данных выборочно или всех данных сразу "
                      "для выбранной записи, выборка происходит по идентификатору номера",
              )
async def change_room_patch(room: Annotated[RoomPath, Path(examples=[{"hotel_id": 1}])],
                            room_params: Annotated[RoomDescriptionOptURL,
                                                   Body(examples=change_room_examples_lst)],
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
    result = await db.rooms.edit(edited_data=room_params,
                                 id=room.room_id,
                                 exclude_unset=True)
    # result = await db.rooms.edit_id(edited_data=room_params,
    #                                 room_id=room.room_id,
    #                                 exclude_unset=True)
    await db.commit()  # Подтверждаем изменение
    return result
