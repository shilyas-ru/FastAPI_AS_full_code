from pydantic import EmailStr
from sqlalchemy import select

from src.repositories.base import BaseRepository

from src.models.users import UsersORM
from src.schemas.users import UserPydanticSchema, UserWithHashedPasswordPydSchm


class UsersRepository(BaseRepository):
    model = UsersORM
    schema = UserPydanticSchema

    # Можно сделать специальный метод, но проще "заточить" в базовом
    # классе репозитория BaseRepositoryMyCode метод get_one_or_none,
    # чтобы его можно было настраивать на конкретную Pydantic схему.
    # Смотри в файле src/api/routers/auth.py функцию login_user_post()
    async def get_user_with_hashed_password(self, email: EmailStr):
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        # result = result.scalars().one()
        result = result.scalars().one_or_none()
        if result:
            return UserWithHashedPasswordPydSchm.model_validate(result)
        return None




    