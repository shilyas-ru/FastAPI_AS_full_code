from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel


# Класс определяет пагинацию, включающую только вывод по страницам
class PaginationPagesListParams(BaseModel):
    # page: Annotated[int | None, Query(None, ge=1)]
    # per_page: Annotated[int | None, Query(None, ge=1, lt=30)]
    page: Annotated[int,
                    Query(ge=1,
                          description="Номер страницы для вывода",
                          )] = 1
    per_page: Annotated[int,
                        Query(ge=1, lt=30,
                              alias="per-page",
                              description="Количество элементов на странице",
                              )] = 3


# Класс определяет пагинацию, включающую вывод по страницам или вывод всего списка сразу
class PaginationPagesAllParams(PaginationPagesListParams):
    all_hotels: Annotated[bool | None,
                          Query(alias="all-hotels",
                                description="Отображать весь список отелей полностью",
                                )] = None


PaginationPagesDep = Annotated[PaginationPagesListParams, Depends()]
PaginationAllDep = Annotated[PaginationPagesAllParams, Depends()]