from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel


# alias="per-page" - позволяет в адресной строке можно указать варианты:
# - http://127.0.0.1:8000/items/?per_page=    это определяется параметром per_page
# - http://127.0.0.1:8000/items/?per-page=    это определяется alias="per-page"

pagination_pages = {"page": 1,
                    "per_page": 3,
                    }


# Класс определяет пагинацию, включающую только вывод по страницам
class PaginationPagesListParams(BaseModel):
    # page: Annotated[int | None, Query(None, ge=1)]
    # per_page: Annotated[int | None, Query(None, ge=1, lt=30)]
    page: Annotated[int,
                    Query(ge=1,
                          description="Номер страницы для вывода (>= 1)",
                          )] = pagination_pages["page"]
    per_page: Annotated[int,
                        Query(ge=1, le=30,
                              alias="per-page",
                              description="Количество элементов на странице (>= 1 и <= 30)",
                              )] = pagination_pages["per_page"]


# Класс определяет пагинацию, включающую вывод по страницам или вывод всего списка сразу
class PaginationPagesAllParams(PaginationPagesListParams):
    all_hotels: Annotated[bool | None,
                          Query(alias="all-hotels",
                                description="Отображать весь список отелей полностью",
                                )] = None


PaginationPagesDep = Annotated[PaginationPagesListParams, Depends()]
PaginationAllDep = Annotated[PaginationPagesAllParams, Depends()]