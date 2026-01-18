from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select

# from src.api.dependencies.dependencies import DBDep
from src.models.bookings import BookingsORM
from src.repositories.base import BaseRepository

from src.schemas.bookings import BookingsPydanticSchema

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


class BookingsRepository(BaseRepository):
    model = BookingsORM
    schema = BookingsPydanticSchema

    # Сделаны методы:
    #
    # - get_all. Выбирает все забронированные номера.
    #       Использует родительский метод get_rows.

    # async def get_all(self, db: DBDep, user_id: int | None = None):
    async def get_all(self, user: BaseModel | None = None):
        """
        Метод класса. Выбирает все забронированные номера.
        Использует родительский метод get_rows.

        :param db: Контекстный менеджер.
        :param user: Идентификатор пользователя, для которого выбирать бронирования.
            Если не указан, то выбираются все имеющиеся бронирования

        :return: Возвращает пустой список: [] или список из выбранных строк:
        [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
         HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
         ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
        Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        """

        query = select(self.model)
        description = "Бронирования номеров не найдены"
        status = "Полный список забронированных номеров."
        if user:
            status = f"Полный список забронированных номеров пользователем {user.email}."
            query = query.filter_by(user_id=user.id)
            description = f"Для пользователя {user.email} бронирования номеров не найдено"

        result = await super().get_rows(query=query,
                                        show_all=True)
        # Возвращает пустой список: [] или список из элементов BookingsPydanticSchema:
        # [BookingsPydanticSchema(room_id=12, user_id=4,
        #                         date_from=datetime.date(2025, 1, 22),
        #                         date_to=datetime.date(2025, 1, 27),
        #                         price=176122, id=1),
        #  BookingsPydanticSchema(room_id=12, user_id=1,
        #                         date_from=datetime.date(2025, 1, 24),
        #                         date_to=datetime.date(2025, 1, 25),
        #                         price=176122, id=2),
        # ...
        #  BookingsPydanticSchema(room_id=12, user_id=1,
        #                         date_from=datetime.date(2025, 1, 24),
        #                         date_to=datetime.date(2025, 1, 25),
        #                         price=176122, id=3)]
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema

        if len(result) == 0:
            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            raise HTTPException(status_code=404,
                                detail={"description": description,
                                        })
        status = (status, f"Всего выводится {len(result)} элемент(-а/-ов).")
        return {"status": status, "rooms": result}
