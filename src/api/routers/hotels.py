from datetime import date

from fastapi import Query, Body, Path, APIRouter
from typing import Annotated

from sqlalchemy import select as sa_select  # Для реализации SQL команды SELECT
from sqlalchemy import delete as sa_delete  # Для реализации SQL команды DELETE

from src.schemas.hotels import HotelPath, HotelDescriptionRecURL, HotelDescriptionOptURL

from src.api.dependencies.dependencies import PaginationPagesDep, PaginationAllDep
from src.api.dependencies.dependencies import DBDep

"""
Рабочие ссылки (список методов, параметры в подробном перечне):
get("/hotels") - Вывод списка всех отелей с разбивкой по страницам или всего 
        списка полностью.
        Выборка реализована через метод select.
        Функция: show_hotels_get
get("/hotels/{hotel_id}") - Получение из базы данных выбранной записи по 
        идентификатору отеля.
        Выборка реализована через метод select.
        Функция: get_hotel_id_get
get("/hotels/find") - Поиск отелей по заданным параметрам и вывод итогового 
        списка с разбивкой по страницам.
        Выборка реализована через метод select.
        Функция: find_hotels_get
        Для поиска реализованы возможности:
          - искать с учётом регистра или не учитывая регистр букв;
          - искать строки, начинающиеся на заданное значение или искать строки, 
            содержащие заданное значение.
delete("/hotels/{hotel_id}") - Удаление выбранной записи по идентификатору отеля.
        Реализовано удаление одного объекта, когда объект для удаления получаем 
        по первичному ключу (метод session.get).
        Удаление выбранной записи реализовано через метод delete.
        Функция: delete_hotel_id_del
delete("/hotels") - Удаление выбранных записей с выборкой по наименованию
        и адресу отеля - что требуется удалять.
        Удаление выбранных записей реализовано через метод delete.
        Функция: delete_hotel_param_del
        Для выбора удаляемых строк реализованы возможности:
        - искать с учётом регистра или не учитывая регистр букв;
        - искать строки, начинающиеся на заданное значение или искать строки, 
          содержащие заданное значение.
        Функция: delete_hotel_param_del
post("/hotels") - Создание записи с новым отелем.
        Создание записи реализовано через метод insert.
        Функция: create_hotel_post
put("/hotels/{hotel_id}") - Обновление ВСЕХ данных одновременно для выбранной записи,
        выборка происходит по идентификатору отеля.
        Обновление реализовано через метод update.
        Функция: change_hotel_put
patch("/hotels/{hotel_id}") - Обновление каких-либо данных выборочно или всех 
        данных сразу для выбранной записи, выборка происходит по идентификатору отеля.
        Реализовано обновление одного объекта, когда объект для обновления 
        получаем по первичному ключу (метод session.get).
        Обновление реализовано через обновление атрибутов 
        объекта: setattr(updated_object, key, value).
        Функция: change_hotel_patch

"""

# Если в списке указывается несколько тегов, то для
# каждого тега создаётся свой раздел в документации
router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("/all",
            summary="Вывод списка всех отелей одновременно с "
                    "разбивкой по страницам или весь список полностью",
            description="Тут будет описание параметров метода",
            )
async def show_hotels_all_get(pagination: PaginationAllDep, db: DBDep):
    """
    ## Функция выводит список всех отелей с разбивкой по страницам или весь список полностью.

    Параметры (передаются методом Query):
    - ***:param** page:* Номер страницы для вывода (должно быть >=1,
                по умолчанию значение 1).
    - ***:param** per_page:* Количество элементов на странице (должно быть
                >=1 и <=30, по умолчанию значение 3).
    - ***:param** all_hotels:* отображать все отели сразу (True), или делать
                вывод постранично (False или None). Может отсутствовать.

    Параметры:
    - ***:param** db:* Контекстный менеджер.

    Если параметр `all_hotels` имеет значение `True`, то остальные
    параметры игнорируются и сразу выводится полный список.

    ***:return:*** Список отелей или строка с уведомлением, если список отель пуст.

    Список отелей выводится в виде:
    list(info: list(str, str), list(dict(hotel_item: HotelItem) | str)), где:
    - ***info***, это две строки:
      - какая страница выводится;
      - сколько элементов на странице;
    - ***list(dict(hotel_item: HotelItem) | str)***, это список выводимых отелей или строка,
    что "Данные отсутствуют".

    ***Пример вывода:***
    ```
    [
     [
      "Страница 1, установлено отображение 3 элемент(-а/-ов) на странице.",
      "Всего выводится 0 элемент(-а/-ов) на странице."
     ],
      "Данные отсутствуют."
    ]
    ```
    или
    ```
    [
     [
      "Полный список отелей.",
      "Всего выводится 23 элемент(-а/-ов) на странице."
     ],
     [
      {
        "title": "Наименование отеля",
        "location": "Адрес отеля",
        "id": 16
      },
      ...
     ]
    ]
    ```
    """

    # if pagination.all_hotels:
    #     return await db.hotels.get_all()
    # else:
    #     return await db.hotels.get_limit(per_page=pagination.per_page,
    #                                      page=pagination.page)
    return await db.hotels.get_limit(per_page=pagination.per_page,
                                     page=pagination.page,
                                     show_all=pagination.all_hotels,
                                     )


@router.get("/free",
            summary="Вывод списка всех отелей одновременно с "
                    "разбивкой по страницам или весь список полностью",
            description="Тут будет описание параметров метода",
            )
async def show_hotels_free_get(pagination: PaginationAllDep,
                               db: DBDep,
                               # check_dates: BookingDateDep,
                               # date_from: date = Query(example='2025-01-20',
                               #                         description="Дата, С которой бронируется номер",
                               #                         default=None),
                               # date_to: date = Query(example='2025-01-23',
                               #                       description="Дата, ДО которой бронируется номер",
                               #                       default=None),
                               date_from: Annotated[date | None,
                                                    Query(example='2025-01-20',
                                                          description="Дата, С которой бронируется номер",
                                                          )] = None,
                               date_to: Annotated[date | None,
                                                  Query(example='2025-01-23',
                                                        description="Дата, ДО которой бронируется номер",
                                                        )] = None
                               ):
    # if pagination.all_hotels:
    #     return await db.hotels.get_limit(date_from=date_from,
    #                                      date_to=date_to,
    #                                      show_all=True)
    #     # return await db.hotels.get_all()
    # else:
    #     return await db.hotels.get_limit(date_from=date_from,
    #                                      date_to=date_to,
    #                                      per_page=pagination.per_page,
    #                                      page=pagination.page,
    #                                      )
    return await db.hotels.get_limit(date_from=date_from,
                                     date_to=date_to,
                                     per_page=pagination.per_page,
                                     page=pagination.page,
                                     show_all=pagination.all_hotels,
                                     )
    # return await db.hotels.get_filtered_by_time(date_from=date_from,
    #                                             date_to=date_to)


@router.get("/find",
            summary="Поиск отелей по заданным параметрам и "
                    "вывод итогового списка с разбивкой по страницам",
            description="Тут будет описание параметров метода",
            )
async def find_hotels_get(pagination: PaginationPagesDep,
                          db: DBDep,
                          hotel_location: Annotated[str | None, Query(min_length=3,
                                                                      description="Адрес отеля",
                                                                      )] = None,
                          hotel_title: Annotated[str | None, Query(min_length=3,
                                                                   description="Название отеля"
                                                                   )] = None,
                          case_sensitivity: Annotated[bool | None,
                                                      Query(alias="case-sensitivity",
                                                            description="Поиск с учётом регистра "
                                                                        "(True) или регистронезависимый "
                                                                        "(False или None)",
                                                            )] = None,
                          starts_with: Annotated[bool | None,
                                                 Query(alias="starts-with",
                                                       description="Поиск строк, начинающихся с "
                                                                   "заданного текста (True), или "
                                                                   "поиск строк, содержащих "
                                                                   "заданный текст (False или None)",
                                                       )] = None,
                          # check_dates: BookingDateAllDep
                          hotels_with_free_rooms: Annotated[bool | None,
                                                            Query(alias="hotels-with-free-rooms",
                                                                  description="Отели со свободными номерами "
                                                                              "в указанные даты "
                                                                              "(True) или полный список отелей "
                                                                              "не учитывая указанные даты"
                                                                              "(False или None)",
                                                                  )] = None,
                          # date_from: date = Query(example='2025-01-20',
                          #                         description="Дата, С которой бронируется номер",
                          #                         default=None),
                          # date_to: date = Query(example='2025-01-23',
                          #                       description="Дата, ДО которой бронируется номер",
                          #                       default=None),
                          date_from: Annotated[date | None,
                                               Query(example='2025-01-20',
                                                     description="Дата, С которой бронируется номер",
                                                     )] = None,
                          date_to: Annotated[date | None,
                                             Query(example='2025-01-23',
                                                   description="Дата, ДО которой бронируется номер",
                                                   )] = None
                          ):
    """
    ## Функция ищет отели по заданным параметрам и выводит информацию о найденных отелях с разбивкой по страницам.

    Параметры:
    - ***:param** db:* Контекстный менеджер.

    Параметры (передаются методом Query):
    - ***:param** hotel_location:* Адрес отеля (может отсутствовать).
    - ***:param** hotel_title:* Название отеля (может отсутствовать).
    - ***:param** case_sensitivity:* Поиск с учётом регистра (True) или
                регистронезависимый (False или None). Может отсутствовать.
    - ***:param** starts_with:* Поиск строк, начинающихся с заданного
                текста (True), или поиск строк, содержащих заданный текст
                (False или None). Может отсутствовать.
    - ***:param** page:* Номер страницы для вывода (должно быть >=1,
                по умолчанию значение 1).
    - ***:param** per_page:* Количество элементов на странице (должно быть
                >=1 и <=30, по умолчанию значение 3).
    - ***:param** hotels_with_free_rooms:* Выбирать отели со свободными
                номерами в указанные даты (True) или выбирать полный список отелей
                не учитывая указанные даты (False или None).
                Может отсутствовать.
    - ***:param** date_from:* Дата, С которой бронируется номер.
            Используется, если параметр hotels_with_free_rooms=True.
    - ***:param** date_to:* Дата, ДО которой бронируется номер.
            Используется, если параметр hotels_with_free_rooms=True.

    ***:return:*** Список отелей или строка с уведомлением, если список отель пуст.

    Один из двух параметров `hotel_location` или `hotel_title` обязан быть задан.

    Значения `case_sensitivity` и `starts_with` влияют на поиск по обоим
    параметрам `hotel_location` и `hotel_title`.

    Если переданы оба параметра `hotel_location` и `hotel_title`, то
    выбираться будет отель, соответствующий обоим параметрам одновременно.

    Список отелей выводится в виде:
    list(info: list(str, str), list(dict(hotel_item: HotelItem) | str)), где:
    - ***info***, это информация, какая страница выводится и сколько элементов на странице;
    - ***list(dict(hotel_item: HotelItem) | str)***, это список выводимых отелей или строка,
    что "Данные отсутствуют".
    """

    query = await db.hotels.create_stmt_for_selection(sql_func=sa_select,
                                                      location={"search_string": hotel_location,
                                                                "case_sensitivity": case_sensitivity,
                                                                "starts_with": starts_with},
                                                      title={"search_string": hotel_title,
                                                             "case_sensitivity": case_sensitivity,
                                                             "starts_with": starts_with},
                                                      order_by=True,
                                                      )
    # if hotels_with_free_rooms:
    #     # Выбирать отели со свободными номерами в указанные даты (True)
    #     if not (date_from and date_to):
    #         # status_code=422: Запрос сформирован правильно, но его невозможно
    #         #                  выполнить из-за семантических ошибок
    #         #                  Unprocessable Content (WebDAV)
    #         raise HTTPException(status_code=422,
    #                             detail={"description": "Не заданы даты для выбора "
    #                                                    "отелей со свободными номерами",
    #                                     })
    # else:
    #     date_from = None,
    #     date_to = None

    return await db.hotels.get_limit(query=query,
                                     per_page=pagination.per_page,
                                     page=pagination.page,
                                     hotels_with_free_rooms=hotels_with_free_rooms,
                                     date_from=date_from,
                                     date_to=date_to,
                                     )


@router.get("/{hotel_id}",
            summary="Получение из базы данных выбранной записи по идентификатору отеля",
            description="Тут будет описание параметров метода",
            )
async def get_hotel_id_get(hotel_path: Annotated[HotelPath, Path()], db: DBDep):
    """
    ## Функция получает из базы данных выбранную запись по идентификатору отеля.

    Параметры (передаются в URL):
    - ***:param** id:* Идентификатор отеля (обязательно).

    Параметры:
    - ***:param** db:* Контекстный менеджер.

    ***:return:*** Возвращает словарь: {"got hotel": dict},
        где:
        - got_hotel: Выбранный объект. Выводятся в виде словаря элементы
            объекта HotelPydanticSchema:
            HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16).
            Тип возвращаемого элемента преобразован к схеме Pydantic: self.schema

        Если элемент, соответствующий hotel_id отсутствует, возбуждается исключение
        HTTPException с кодом 404.
    """

    result = await db.hotels.get_id(hotel_id=hotel_path.hotel_id)
    return result


@router.delete("/{hotel_id}",
               summary="Удаление выбранной записи по идентификатору отеля",
               description="Тут будет описание параметров метода",
               )
async def delete_hotel_id_del(hotel_path: Annotated[HotelPath, Path()], db: DBDep):
    """
    ## Функция удаляет выбранную запись.

    Параметры (передаются в URL):
    - ***:param** id:* Идентификатор отеля (обязательно).

    Параметры:
    - ***:param** db:* Контекстный менеджер.

    ***:return:*** Возвращает словарь:
            {"deleted hotels": list(dict)},
            где:
            - deleted_hotels: Список с удалёнными элементами:
                  [HotelPydanticSchema(title='title_string_1',
                                       location='location_string_1', id=16),
                   HotelPydanticSchema(title='title_string_2',
                                       location='location_string_2', id=17),
                   ..., HotelPydanticSchema(title='title_string_N',
                                            location='location_string_N', id=198)]
                  Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema

        Если элементы, соответствующие запросу на удаление в параметре delete_stmt
        и фильтрам, указанным в **filtering, отсутствуют, возбуждается исключение
        HTTPException с кодом 404.
    """

    result = await db.hotels.delete(id=hotel_path.hotel_id)
    await db.commit()  # Подтверждаем изменение
    return result


@router.delete("",
               summary="Удаление выбранных записей с выборкой по наименованию "
                       "и адресу отеля - что требуется удалять",
               description="Тут будет описание параметров метода",
               )
async def delete_hotel_param_del(db: DBDep,
                                 hotel_location: Annotated[str | None, Query(min_length=3,
                                                                             description="Адрес отеля",
                                                                             )] = None,
                                 hotel_title: Annotated[str | None, Query(min_length=3,
                                                                          description="Название отеля"
                                                                          )] = None,
                                 case_sensitivity: Annotated[bool | None,
                                                             Query(alias="case-sensitivity",
                                                                   description="Поиск с учётом регистра "
                                                                               "(True) или регистронезависимый "
                                                                               "(False или None)",
                                                                   )] = None,
                                 starts_with: Annotated[bool | None,
                                                        Query(alias="starts-with",
                                                              description="Поиск строк, начинающихся с "
                                                                          "заданного текста (True), или "
                                                                          "поиск строк, содержащих "
                                                                          "заданный текст (False или None)",
                                                              )] = None,
                                 ):
    """
    ## Функция удаляет выбранную запись или записи с выборкой, что удалять, по наименованию и адресу отеля.

    Параметры:
    - ***:param** db:* Контекстный менеджер.

    Параметры (передаются методом Query):
    - ***:param** hotel_location:* Адрес отеля (может отсутствовать).
    - ***:param** hotel_title:* Название отеля (может отсутствовать).
    - ***:param** case_sensitivity:* Поиск с учётом регистра (True) или
         регистронезависимый (False или None). Может отсутствовать.
    - ***:param** starts_with:* Поиск строк, начинающихся с заданного
         текста (True), или поиск строк, содержащих заданный текст
         (False или None). Может отсутствовать.

        :return: Возвращает словарь:
            {"deleted hotels": list(dict)},
            где:
            - deleted_hotels: Список с удалёнными элементами:
                  [HotelPydanticSchema(title='title_string_1',
                                       location='location_string_1', id=16),
                   HotelPydanticSchema(title='title_string_2',
                                       location='location_string_2', id=17),
                   ..., HotelPydanticSchema(title='title_string_N',
                                            location='location_string_N', id=198)]
                  Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema

        Если элементы, соответствующие запросу на удаление в параметре delete_stmt
        и фильтрам, указанным в **filtering, отсутствуют, возбуждается исключение
        HTTPException с кодом 404.

    Один из двух параметров `hotel_location` или `hotel_title` обязан быть задан.

    Значения `case_sensitivity` и `starts_with` влияют на поиск по обоим
    параметрам `hotel_location` и `hotel_title`.

    Если переданы оба параметра `hotel_location` и `hotel_title`, то
    выбираться будет отель, соответствующий обоим параметрам одновременно.

    """

    stmt = await db.hotels.create_stmt_for_selection(sql_func=sa_delete,
                                                     location={"search_string": hotel_location,
                                                               "case_sensitivity": case_sensitivity,
                                                               "starts_with": starts_with},
                                                     title={"search_string": hotel_title,
                                                            "case_sensitivity": case_sensitivity,
                                                            "starts_with": starts_with},
                                                     )

    result = await db.hotels.delete(delete_stmt=stmt)
    await db.commit()  # Подтверждаем изменения
    return result


openapi_examples_dict = {"1": {"summary": "Сочи",
                               "value": {"title": "title Сочи",
                                         "location": "location Сочи"
                                         }
                               },
                         "2": {"summary": "Дубай",
                               "value": {"title": "title Дубай",
                                         "location": "location Дубай"
                                         }
                               }
                         }


@router.post("",
             summary="Создание записи с новым отелем",
             description="Тут будет описание параметров метода",
             )
async def create_hotel_post(db: DBDep,
                            hotel_caption: Annotated[HotelDescriptionRecURL,
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
    result = await db.hotels.add(hotel_caption)
    await db.commit()
    return {"added data": result}


@router.put("/{hotel_id}",
            summary="Обновление ВСЕХ данных одновременно для выбранной "
                    "записи, выборка происходит по идентификатору отеля",
            description="Тут будет описание параметров метода",
            )
async def change_hotel_put(hotel_path: Annotated[HotelPath, Path()],
                           hotel_caption: Annotated[HotelDescriptionRecURL, Body()],
                           db: DBDep,
                           ):
    """
    ## Функция изменяет (обновляет) ВСЕ данные одновременно

    В ручке PUT мы обязаны передать оба параметра title и location.

    Параметры (передаются в URL):
    - ***:param** hotel_id:* Идентификатор отеля (обязательно).

    Параметры (передаются методом Body):
    - ***:param** title:* Название отеля (обязательно).
    - ***:param** location:* Адрес отеля (обязательно).

    Параметры:
    - ***:param** db:* Контекстный менеджер.

    ***:return:*** Возвращает словарь:
                {"status": status, "err_type": err_type, "updated rows": updated_rows},
                где:
                - status: str. Текстовое описание результата операции.
                - err_type: int. Код результата операции.
                  Принимает значения:
                  - 0 (OK - выполнено нормально, без ошибок).
                  - 1 (Для объекта с указанным идентификатором ничего не найдено).
                - updated_rows. Список, содержащий отредактированный объект. Выводится
                  в виде списка, содержащего элементы объекта HotelsORM.
    """

    result = await db.hotels.edit(edited_data=hotel_caption,
                                  id=hotel_path.hotel_id)
    # result = await db.hotels.edit_id(edited_data=hotel_caption,
    #                                  object_id=hotel_path.hotel_id)
    await db.commit()  # Подтверждаем изменение
    return result


@router.patch("/{hotel_id}",
              summary="Обновление каких-либо данных выборочно или всех данных сразу "
                      "для выбранной записи, выборка происходит по идентификатору отеля",
              description="Тут будет описание параметров метода",
              )
# Тут параметр examples переопределяет то, что определено в схеме в параметре
# examples в классе HotelDescriptionOptURL в файле src\schemas\hotels.py
async def change_hotel_patch(hotel_path: Annotated[HotelPath, Path(examples=[{"hotel_id": 1
                                                                              }
                                                                             ]
                                                                   )],
                             hotel_caption: Annotated[HotelDescriptionOptURL,
                                                      Body(examples=[{
                                                          "title": "Название отеля",
                                                          "location": "Адрес отеля",
                                                                      },
                                                                     ]
                                                           )
                                                      ],
                             db: DBDep,
                             ):
    """
    ## Функция обновляет каких-либо данные выборочно или все данных сразу

    В PATCH ручке можем передать либо только title, либо только location,
    либо оба параметра сразу (тогда PATCH ничем не отличается от PUT ручки).

    Параметры (передаются в URL):
    - ***:param** hotel_id:* Идентификатор отеля (обязательно).

    Параметры (передаются методом Body):
    - ***:param** title:* Название отеля (необязательно, не
            указан - изменяться не будет).
    - ***:param** location:* Местонахождение (адрес) отеля
            (необязательно, не указан - изменяться не будет).

    Параметры:
    - ***:param** db:* Контекстный менеджер.

    ***:return:*** Статус завершения операции (текст) и значение
            статуса операции (число): 0, 1

    Значение статуса завершения операции:
    - 0: все OK.
    - 1: ничего не найдено.
    """

    err_type = 1
    status = f"Для отеля с идентификатором {hotel_path.hotel_id} ничего не найдено"

    if not (hotel_caption.title or hotel_caption.location):
        status = "Не заданы параметры для выбора отеля"
        return {"status": status, "err_type": err_type}

    # result = await db.hotels.edit(edited_data=hotel_caption,
    #                               exclude_unset=True,
    #                               id=hotel_path.hotel_id)
    result = await db.hotels.edit_id(edited_data=hotel_caption,
                                     exclude_unset=True,
                                     object_id=hotel_path.hotel_id)
    await db.commit()  # Подтверждаем изменение
    return result
