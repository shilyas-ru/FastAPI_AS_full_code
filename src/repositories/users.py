from src.repositories.base import BaseRepository

from src.models.users import UsersORM
from src.schemas.users import UserPydanticSchema


class UsersRepository(BaseRepository):
    model = UsersORM
    schema = UserPydanticSchema

    