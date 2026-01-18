from fastapi import Body, Path, APIRouter, HTTPException
from typing import Annotated

from src.api.dependencies.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingsRoomPath, BookingsInfoRecRequest, BookingsInfoRecURL, BookingsInfoRecFull

"""
- Полное именование URL:
    - /bookings/hotels/{hotel_id}/rooms/{rooms_id}
    Используется, если требуется указать идентификатор отеля и идентификатор номера.
- Именование URL для поиска свободных номеров в указанном отеле:
    - /bookings/hotels/{hotel_id}/free/find
- Именование URL для поиска свободных номеров по параметрам номера:
    - /bookings/hotels/{hotel_id}/rooms/free/find
    - /bookings/hotels/{hotel_id}/free

    - /bookings/hotels/{hotel_id}/rooms/{rooms_id}
    
    - /hotels/{hotel_id}/rooms/{rooms_id}
    - /hotels/rooms/{rooms_id}
    Используется, если требуется указать идентификатор номера, а идентификатор отеля 
    в адресе не указывается.
    Такой вариант может использоваться, если идентификатор отеля передаётся в другом 
    запросе, например, через тело запроса.

- Необходимо реализовать для бронирования для конкретного пользователя (из куков) 
  за указанный временной диапазон:
    1. Добавить бронирование номера по конкретному номеру по id номера
       Метод get:  
            /bookings/rooms/{rooms_id}
            /bookings/hotels/{hotel_id}/rooms/{rooms_id}
    2. Изменять бронирование номера post (все поля сразу)
       Метод post:  
            /bookings/hotels/{hotel_id}/rooms/{rooms_id}
    3. Изменять бронирование номера patch (какие-то поля выборочно или все поля сразу)
       Метод patch:  
            /bookings/hotels/{hotel_id}/rooms/{rooms_id}
    4. Удалять бронирование номера
       Метод delete:  
            /bookings/hotels/{hotel_id}/rooms/{rooms_id}

    5. Вывести информацию по всем свободным номерам отеля по конкретному отелю по id отеля
       Метод get:  
            /bookings/hotels/{hotel_id}/free
    6. Вывести инфо (занят/свободен) по конкретному номеру по id номера
       Метод get:  
            /bookings/hotels/{hotel_id}/rooms/{rooms_id}
    
- Сделать по возможности:
    7. Вывести информацию по всем свободным номерам отеля по конкретному отелю по title отеля 
       и/или по location отеля
       Метод get:  
            /bookings/hotels/{hotel_id}/free/find
    8. Вывести инфо (занят/свободен) по конкретному номеру по title номера и/или по 
       description номера
       Метод get:  
            /bookings/hotels/{hotel_id}/rooms/free/find

"""

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.post("/rooms/{room_id}",
             summary="Создание записи о новом бронировании номера в отеле",
             )
async def create_booking_room_id_post(roompath: Annotated[BookingsRoomPath, Path()],
                                      booking_params: Annotated[BookingsInfoRecRequest,
                                                                Body()],
                                      user_id: UserIdDep,
                                      db: DBDep):
    """
    ## Функция создаёт запись о бронировании номера.
    :return:
    """
    # Определяем идентификатор пользователя - user_id передаётся из UserIdDep
    if not user_id:
        # Пользователь не авторизовался
        # status_code=401: не аутентифицирован
        raise HTTPException(status_code=401,
                            detail="Пользователь не авторизовался")

    # Получаем цену номера - смотрим таблицу rooms
    room = await db.rooms.get_one_or_none(id=roompath.room_id)

    if not room:
        # status_code=404: Сервер понял запрос, но не нашёл
        #                  соответствующего ресурса по указанному URL
        raise HTTPException(status_code=404,
                            detail={"description": "Нет номера с идентификатором "
                                                   f"{roompath.room_id}",
                                    })
    price = room.price

    # Теоретически, сейчас надо проверить, что номера в доступе имеются и
    # что по указанным датам они свободны. Практически, мы это не проверяем.

    # Создаем схему данных с ценой и пользователем - все поля, кроме id
    _booking_params = BookingsInfoRecFull(room_id=roompath.room_id,
                                          user_id=user_id,
                                          price=price,
                                          **booking_params.model_dump())
    # Добавляем бронирование пользователю
    booking = await db.bookings.add(_booking_params)
    await db.commit()
    return {"booking": booking}
