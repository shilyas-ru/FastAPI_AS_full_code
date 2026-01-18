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

    # Сделаны методы:
    #
    # - get_user_with_hashed_password. Выбирает пользователя по email.

    # Можно сделать специальный метод, но проще "заточить" в базовом
    # классе репозитория BaseRepository метод get_one_or_none, чтобы
    # его можно было настраивать на конкретную Pydantic схему.
    # Смотри в файле src/api/routers/auth.py функцию login_user_post()
    async def get_user_with_hashed_password(self, email: EmailStr):
        """
        По факту метод не используется.
        Вместо него используется метод get_one_or_none из BaseRepository (базового репозитария):
            user = await db.users.get_one_or_none(pydantic_schema=UserWithHashedPasswordPydSchm,
                                                  email=user_info.email)
        Метод класса. Выбирает пользователя по email.

        :param email: Электронная почта пользователя для поиска пользователя.
        :return: Возвращается
            - если пользователь не найден: None;
            - найденный пользователь:
                UserWithHashedPasswordPydSchm(id=4,
                                              email='user@example.com',
                                              hashed_password='$2b$12$Hvd4XKN2wN3S1sIMnC0Iu.TCtaZ/br7eWKClms0C6QuIBdJm2LMK6'
                                              )
        """
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        # result = result.scalars().one()
        result = result.scalars().one_or_none()
        # result: <src.models.users.UsersORM object at 0x000001958B0EC5D0>
        if result:
            # Возвращается объект, преобразованный к UserWithHashedPasswordPydSchm :
            # UserWithHashedPasswordPydSchm(id=4,
            #                               email='user@example.com',
            #                               hashed_password='$2b$12$Hvd4XKN2wN3S1sIMnC0Iu.TCtaZ/br7eWKClms0C6QuIBdJm2LMK6'
            #                               )
            return UserWithHashedPasswordPydSchm.model_validate(result)
        return None




    