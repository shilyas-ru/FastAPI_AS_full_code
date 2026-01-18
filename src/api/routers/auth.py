from fastapi import APIRouter, HTTPException, Response
from sqlalchemy.exc import IntegrityError

from src.api.dependencies.dependencies import UserIdDep
from src.database import async_session_maker
from src.repositories.users import UsersRepository
from src.schemas.users import UserDescriptionRecURL, UserBase, UserWithHashedPasswordPydSchm
from src.services.auth import AuthService

# Устанавливаем библиотеки: pip install pyjwt "passlib[bcrypt]"
# https://fastapi.qubitpi.org/tutorial/security/oauth2-jwt/

"""
Рабочие ссылки (список методов, параметры в подробном перечне):
post("/auth/login") - Проверка, что пользователь существует и может 
        авторизоваться.
        Функция: login_user_post
post("/auth/register") - Создание записи с новым пользователем.
        Функция: register_user_post
post("/auth/only_auth") - Тестовый метод для получения куков по имени 
        (в примере проверяется значение для access_token).
        Функция: only_auth
"""

# Если в списке указывается несколько тегов, то для
# каждого тега создаётся свой раздел в документации
router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register",
             summary="Создание записи с новым пользователем",
             )
async def register_user_post(user_info: UserDescriptionRecURL):
    """
    ## Функция создаёт запись с новым пользователем.

    Параметры (передаются методом Body):
    - ***:param** email:* Электронная почта (обязательно)
    - ***:param** password:* Пароль (обязательно)

    ***:return:*** Словарь: `dict("status": status, "added data": added_user)`, где
    - *status*: str. Статус завершения операции.
    - *added_user*: UserPydanticSchema. Запись с добавленными данными.
      Тип возвращаемых элементов преобразован к указанной схеме Pydantic.

    В текущей реализации статус завершения операции всегда один и тот же: OK
    """
    hashed_password = AuthService().hashed_password(user_info.password)
    new_user_info = UserBase(email=user_info.email, hashed_password=hashed_password)

    # При попытке добавить пользователя с уже существующим в БД
    # email будет ошибка (отрабатывается на уровне базы данных):
    # sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.UniqueViolationError'>: повторяющееся значение ключа нарушает ограничение уникальности "users_email_key"
    # DETAIL:  Ключ "(email)=(string@gf.rt)" уже существует.
    # [SQL: INSERT INTO users (email, hashed_password) VALUES ($1::VARCHAR, $2::VARCHAR) RETURNING users.id, users.email, users.hashed_password]
    # [parameters: ('string@gf.rt', '$2b$12$UAgsjvDqbnxsOanT4yFI3u2LqzMlEDrhylikYNa92CzS6M8rsu3Ne')]
    # (Background on this error at: https://sqlalche.me/e/20/gkpj)
    async with async_session_maker() as session:
        try:
            result = await UsersRepository(session).add(new_user_info)
            await session.commit()
        except IntegrityError:
            return {"status": "Fail",
                    "added data": f"Пользователь с email {user_info.email} уже существует."}
        status = "OK"
    return {"status": status, "added data": result}


@router.post("/login",
             summary="Авторизация пользователя",
             )
async def login_user_post(user_info: UserDescriptionRecURL,
                          response: Response):
    """
    ## Функция проверяет, что пользователь существует и может авторизоваться, при успехе происходит авторизация пользователя.

    Параметры (передаются методом Body):
    - ***:param** email:* Электронная почта (обязательно)
    - ***:param** password:* Пароль (обязательно)
    - ***:param** response:* Ответ, который идёт пользователю

    ***:return:*** Словарь: `dict("status": status, "access token": access_token)`, где
    - *status*: str. Статус завершения операции.
    - *access_token*: UserPydanticSchema. Запись с добавленными данными.
      Тип возвращаемых элементов преобразован к указанной схеме Pydantic.

    В текущей реализации статус завершения операции всегда один и тот же: OK
    """
    async with async_session_maker() as session:
        # Можно сделать специальный метод, но проще "заточить" в базовом
        # классе репозитория BaseRepositoryMyCode метод get_one_or_none,
        # чтобы его можно было настраивать на конкретную Pydantic схему.
        # user = await UsersRepository(session).get_user_with_hashed_password(email=user_info.email)
        user = await UsersRepository(session).get_one_or_none(pydantic_schema=UserWithHashedPasswordPydSchm,
                                                              email=user_info.email)
        # user - это Pydantic схема UserPydanticSchema
        if not user:
            # Пользователь с таким email уже имеется
            # status_code=401: не аутентифицирован
            raise HTTPException(status_code=401,
                                detail="Пользователь с таким email не зарегистрирован")

        if not AuthService().verify_password(user_info.password, user.hashed_password):
            raise HTTPException(status_code=401,
                                detail="Пароль не верный")

        # validity_period - словарь, ключи которого должны совпадать с параметрами функции:
        # timedelta(days=0, seconds=0, microseconds=0,
        #           milliseconds=0, minutes=0, hours=0, weeks=0)
        # Можно не указывать значение validity_period:
        # access_token = AuthService().create_access_token(data={"user_id": user.id})
        # тогда длительность будет установлена по
        # умолчанию: minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        validity_period = {"hours": 1, "minutes": 30}
        access_token = AuthService().create_access_token(data={"user_id": user.id},
                                                         validity_period=validity_period)
        status = "OK"
        response.set_cookie("access_token", access_token)  # отправили в куки
    return {"status": status, "access_token": access_token}  # отправили клиенту


@router.get("/get_me",
            summary="Получение информации о текущем авторизованном пользователе",
            )
async def get_me_get(user_id: UserIdDep):
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_id(object_id=user_id)
    return user_id, user


@router.delete("/logout",
               summary="Выход авторизованного пользователя",
               )
async def get_me_delete(response: Response):
    response.delete_cookie("access_token")
    return {"status": "OK"}
