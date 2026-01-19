from datetime import date
from typing import Annotated, Union

from fastapi import Depends, Query, Request, HTTPException
from pydantic import BaseModel, Field

from src.api.dependencies.dependencies_consts import pagination_pages
from src.database import async_session_maker
from src.services.auth import AuthService
from src.utils.db_manager import DBManager

# src\api\dependencies\dependencies-consts.py
# alias="per-page" - позволяет в адресной строке можно указать варианты:
# - http://127.0.0.1:8000/items/?per_page=    это определяется параметром per_page
# - http://127.0.0.1:8000/items/?per-page=    это определяется alias="per-page"

# from src.api.dependencies.dependencies import pagination_pages
# pagination_pages = {"page": 1,
#                     "per_page": 3,
#                     }
# Файлы, где используются pagination_pages:
#   - \src\api\dependencies\dependencies.py
#      В классе PaginationPagesListParams при задании значений по
#      умолчанию для параметров page и per_page
#   - \src\repositories\base.py
#      В async def get_rows при задании значений по
#      умолчанию для параметров page и per_page


# Класс определяет пагинацию, включающую только вывод по страницам
class PaginationPagesParams(BaseModel):
    # Если использовать следующий синтаксис, то чтобы отображались все описания description
    # надо использовать:
    # PaginationAllDep = Annotated[PaginationPagesParams, Query()]
    #
    # page: Annotated[int | None, Query(None, ge=1)]
    # per_page: Annotated[int | None, Query(None, ge=1, lt=30)]
    # page: Annotated[int,
    #                 Query(ge=1,
    #                       description="Номер страницы для вывода (>= 1).<br>"
    #                                   "<b><i>Не используется, если параметр "
    #                                   "all-objects равен True.</i></b>",
    #                       )] = pagination_pages["page"]
    # per_page: Annotated[int,
    #                     Query(ge=1,
    #                           le=30,
    #                           alias="per-page",
    #                           description="Количество элементов на странице (>= 1 и <= 30).<br>"
    #                                       "<b><i>Не используется, если параметр "
    #                                       "all-objects равен True.</i></b>",
    #                           )] = pagination_pages["per_page"]

    # Если использовать следующий синтаксис, то чтобы отображались все описания description
    # надо использовать:
    # PaginationPagesDep = Annotated[PaginationPagesParams, Depends()]
    #
    page: int = Field(Query(ge=1,
                            description="Номер страницы для вывода (>= 1).",
                            default=pagination_pages["page"],
                            )
                      )
    per_page: int = Field(Query(ge=1,
                                le=30,
                                alias="per-page",
                                description="Количество элементов на странице (>= 1 и <= 30).",
                                default=pagination_pages["per_page"],
                                )
                          )


# Класс определяет пагинацию, включающую вывод по страницам или вывод всего списка сразу
class PaginationPagesAllParams(PaginationPagesParams):
    # Если использовать следующий синтаксис, то чтобы отображались все описания description
    # надо использовать:
    # PaginationAllDep = Annotated[PaginationPagesAllParams, Query()]
    #
    # all_objects: Annotated[bool | None,
    #                        Query(alias="all-objects",
    #                              description="Отображать весь список сразу (True), игнорируя "
    #                                          "параметры page и per-page,<br>"
    #                                          "или делать вывод постранично (False или None), "
    #                                          "учитывая параметры page и per-page.<br>"
    #                                          "<b><i>Может отсутствовать.</i></b>",
    #                              )] = None

    # Если использовать следующий синтаксис, то чтобы отображались все описания description
    # надо использовать:
    # PaginationPagesDep = Annotated[PaginationPagesAllParams, Depends()]
    #
    all_objects: bool | None = Field(Query(default=None,
                                           alias="all-objects",
                                           description="Отображать весь список сразу (True), игнорируя "
                                                       "параметры page и per-page,<br>"
                                                       "или делать вывод постранично (False или None), "
                                                       "учитывая параметры page и per-page.<br>"
                                                       "<b><i>Может отсутствовать.</i></b>",
                                           )
                                     )

# Set description for query parameter in swagger doc using Pydantic model (FastAPI)
# https://stackoverflow.com/questions/64364499/set-description-for-query-parameter-in-swagger-doc-using-pydantic-model-fastapi
# How to define query parameters using Pydantic model in FastAPI?
# https://stackoverflow.com/questions/75998227/how-to-define-query-parameters-using-pydantic-model-in-fastapi
# Вывод:
# To add description, title, etc., to query parameters, you could wrap the Query() in a Field().
# Чтобы добавить описание, заголовок и т.д. к параметрам запроса, вы можете обернуть Query() в Field()


# Используется, если поля описывать как - page: int = Field(Query(ge=1,...
# (тогда будут отображаться все описания description):
PaginationPagesDep = Annotated[PaginationPagesParams, Depends()]

# Используется, если поля описывать как - per_page: Annotated[int, Query(ge=1,...
# (тогда будут отображаться все описания description):
# PaginationPagesDep = Annotated[PaginationPagesParams, Query()]


# Используется, если поля описывать как - page: int = Field(Query(ge=1,...
# (тогда будут отображаться все описания description):
PaginationAllDep = Annotated[PaginationPagesAllParams, Depends()]

# Используется, если поля описывать как - per_page: Annotated[int, Query(ge=1,...
# (тогда будут отображаться все описания description):
# PaginationAllDep = Annotated[PaginationPagesAllParams, Query()]


def get_token(request: Request) -> str:
    token = request.cookies.get('access_token', None)
    if not token:
        raise HTTPException(status_code=401,
                            detail="Не предоставлен токен доступа")
    return token


def get_current_user_id(token: str = Depends(get_token)) -> Union[int, None]:
    data = AuthService().decode_token(token)
    user_id = data.get("user_id", None)
    return user_id


UserIdDep = Annotated[int, Depends(get_current_user_id)]


def get_db_manager():
    return DBManager(session_factory=async_session_maker)


async def get_db():
    # Можно не использовать функцию get_db_manager(), а сразу написать:
    # async with DBManager(session_factory=async_session_maker) as db:
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]
