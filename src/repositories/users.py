from pydantic import EmailStr
from sqlalchemy import select

from src.repositories.base import BaseRepository

from src.models.users import UsersORM
from src.schemas.users import UserPydanticSchema, UserWithHashedPasswordPydSchm

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


class UsersRepository(BaseRepository):
    model = UsersORM
    schema = UserPydanticSchema

    # Можно сделать специальный метод, но проще "заточить" в базовом
    # классе репозитория BaseRepository метод get_one_or_none, чтобы
    # его можно было настраивать на конкретную Pydantic схему.
    # Смотри в файле src/api/routers/auth.py функцию login_user_post()
    async def get_user_with_hashed_password(self, email: EmailStr):
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        # result = result.scalars().one()
        result = result.scalars().one_or_none()
        if result:
            return UserWithHashedPasswordPydSchm.model_validate(result)
        return None




    