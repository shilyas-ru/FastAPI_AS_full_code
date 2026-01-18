from datetime import date

from pydantic import EmailStr
from sqlalchemy import select

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

