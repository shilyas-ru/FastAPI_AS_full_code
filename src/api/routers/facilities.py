from datetime import date

from fastapi import Body, Path, APIRouter, Query
from typing import Annotated

from sqlalchemy import select as sa_select  # Для реализации SQL команды SELECT
from sqlalchemy import delete as sa_delete  # Для реализации SQL команды DELETE

from src.api.dependencies.dependencies import DBDep, PaginationAllDep, PaginationPagesAllParams
from src.schemas.facilities import FacilityDescriptionRecURL

# from src.schemas.facilities import


# Если в списке указывается несколько тегов, то для
# каждого тега создаётся свой раздел в документации
router = APIRouter(prefix="/facilities", tags=["Удобства"])


#     GET /facilities на получение всех удобств
#     POST /facilities для добавления нового удобства

@router.get("",
            summary="Вывод удобств в номерах - весь список полностью",
            description="Тут будет описание параметров метода",
            )
# async def show_rooms_in_hotel_get(hotel_id: Path()):
# async def show_facilities_in_rooms_get(pagination: PaginationPagesAllParams,
# async def show_facilities_in_rooms_get(pagination: Annotated[PaginationPagesAllParams, Query()],
async def show_facilities_in_rooms_get(db: DBDep,
                                       pagination: PaginationAllDep,
                                       # pagination: PaginationPagesAllParams = Query(),
                                       # pagination: Annotated[PaginationPagesAllParams, Query()],

                                       ):
    return await db.facilities.get_limit(per_page=pagination.per_page,
                                         page=pagination.page,
                                         show_all=pagination.all_objects,
                                         )


openapi_examples_dict = {"1": {"summary": "Кабельный интернет",
                               "value": {"title": "title Кабельный интернет",
                                         }
                               },
                         "2": {"summary": "Wi-Fi",
                               "value": {"title": "title Wi-Fi",
                                         }
                               },
                         "3": {"summary": "Стационарный телефон",
                               "value": {"title": "title Стационарный телефон",
                                         }
                               },
                         }


@router.post("",
             summary="Создание записи с новыми удобствами в номере",
             description="Тут будет описание параметров метода",
             )
async def create_facility_post(db: DBDep,
                               facility_caption: Annotated[FacilityDescriptionRecURL,
                                                           Body(openapi_examples=openapi_examples_dict)]):
    """
    ## Функция создаёт запись.

    Параметры:
    - ***:param** db:* Контекстный менеджер.

    Параметры (передаются методом Body):
    - ***:param** title:* Название отеля (обязательно)
    - ***:param** location:* Местонахождение отеля (обязательно)

    ***:return:*** Словарь: `dict("status": status, "added data": added_hotel)`, где
        - *status*: str. Статус завершения операции.
        - *added_hotel*: HotelPydanticSchema. Запись с добавленными данными.
          Тип возвращаемых элементов преобразован к указанной схеме Pydantic.

    В текущей реализации статус завершения операции всегда один и тот же: OK
    """
    # преобразуют модель в словарь Python: HotelDescriptionRecURL.model_dump()
    # Раскрываем (распаковываем) словарь в список именованных аргументов
    # "title"= , "location"=
    # add_hotel_stmt = insert(HotelsORM).values(**hotel_caption.model_dump())
    # result = await session.execute(add_hotel_stmt)
    # add_id = result.scalars().all()[0]
    result = await db.facilities.add(facility_caption)
    await db.commit()
    return {"added data": result}

