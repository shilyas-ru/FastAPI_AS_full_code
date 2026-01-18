from typing import Annotated

from fastapi import APIRouter, Body

from src.database import async_session_maker
from src.repositories.users import UsersRepository
from src.schemas.users import UserDescriptionRecURL, UserBase

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Устанавливаем библиотеки: pip install pyjwt "passlib[bcrypt]"
# https://fastapi.qubitpi.org/tutorial/security/oauth2-jwt/

# Если в списке указывается несколько тегов, то для
# каждого тега создаётся свой раздел в документации
router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register",
             summary="Создание записи с новым пользователем",
             )
async def register_user_post(user_info: UserDescriptionRecURL):
    """
    ## Функция создаёт запись.

    Параметры (передаются методом Body):
    - ***:param** email:* Электронная почта (обязательно)
    - ***:param** password:* Пароль (обязательно)

    ***:return:*** Словарь: `dict("status": status, "added data": added_user)`, где
        - *status*: str. Статус завершения операции.
        - *added_user*: UserPydanticSchema. Запись с добавленными данными.
          Тип возвращаемых элементов преобразован к указанной схеме Pydantic.

    В текущей реализации статус завершения операции всегда один и тот же: OK
    """
    hashed_password = pwd_context.hash(user_info.password)
    new_user_info = UserBase(email=user_info.email, hashed_password=hashed_password)

    # При попытке добавить пользователя с уже существующим в БД
    # email будет ошибка (отрабатывается на уровне базы данных):
    # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.UniqueViolationError'>: повторяющееся значение ключа нарушает ограничение уникальности "users_email_key"
    # DETAIL:  Ключ "(email)=(string@gf.rt)" уже существует.
    # [SQL: INSERT INTO users (email, hashed_password) VALUES ($1::VARCHAR, $2::VARCHAR) RETURNING users.id, users.email, users.hashed_password]
    # [parameters: ('string@gf.rt', '$2b$12$UAgsjvDqbnxsOanT4yFI3u2LqzMlEDrhylikYNa92CzS6M8rsu3Ne')]
    # (Background on this error at: https://sqlalche.me/e/20/gkpj)
    async with async_session_maker() as session:
        result = await UsersRepository(session).add(new_user_info)
        await session.commit()
        status = "OK"
    return {"status": status, "added data": result}
