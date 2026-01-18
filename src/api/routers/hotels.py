from fastapi import Query, Body, Path, APIRouter
from typing import Annotated

from src.models.hotels import HotelsORM
from src.repositories.hotels import HotelsRepository
from src.schemas.hotels import HotelPath, HotelDescriptionRecURL, HotelDescriptionOptURL

from src.api.dependencies.dependencies import PaginationPagesDep, PaginationAllDep
from src.database import async_session_maker, engine
from sqlalchemy import insert  # Для реализации SQL команды INSERT
from sqlalchemy import select  # Для реализации SQL команды SELECT
from sqlalchemy import delete  # Для реализации SQL команды DELETE
from sqlalchemy import update  # Для реализации SQL команды UPDATE

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


@router.get("",
            summary="Вывод списка всех отелей одновременно с "
                    "разбивкой по страницам или весь список полностью",
            )
async def show_hotels_get(pagination: PaginationAllDep):
    """
    ## Функция выводит список всех отелей с разбивкой по страницам или весь список полностью.

    Параметры (передаются методом Query):
    - ***:param** page:* Номер страницы для вывода (должно быть >=1,
                по умолчанию значение 1).
    - ***:param** per_page:* Количество элементов на странице (должно быть
                >=1 и <=30, по умолчанию значение 3).
    - ***:param** all_hotels:* отображать все отели сразу (True), или делать
                вывод постранично (False или None). Может отсутствовать.

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
    f = [
        [
            "Страница 1, установлено отображение 3 элемент(-а/-ов) на странице.",
            "Всего выводится 0 элемент(-а/-ов) на странице."
        ],
        "Данные отсутствуют."
    ]
    # get_hotels_query = select(HotelsORM)
    # if not pagination.all_hotels:
    #     skip = (pagination.page - 1) * pagination.per_page
    #     get_hotels_query = (get_hotels_query
    #                         .limit(pagination.per_page)
    #                         .offset(skip)
    #                         )
    #
    # async with async_session_maker() as session:
    #     result = await session.execute(get_hotels_query)
    #     hotels_lst = result.scalars().all()
    #
    # if pagination.all_hotels:
    #     status = "Полный список отелей."
    # else:
    #     status = (f"Страница {pagination.page}, установлено отображение {pagination.per_page} "
    #               f"элемент(-а/-ов) на странице.")
    # status = (status, f"Всего выводится {len(hotels_lst)} элемент(-а/-ов) на странице.")
    # if len(hotels_lst) == 0:
    #     status = (status, f"Данные отсутствуют.")
    # else:
    #     status = (status, hotels_lst)
    #
    # return status

    async with async_session_maker() as session:
        # return await HotelsRepository(session,
        #                               HotelsORM).get_all(limit=pagination.per_page,
        #                                                  offset=(pagination.page - 1) * pagination.per_page)
        # return await HotelsRepository(session).get_one_or_none(title="ффф")
        # return await HotelsRepository(session).get_all()
        if pagination.all_hotels:
            return await HotelsRepository(session).get_all()
        else:
            # return await HotelsRepository(session).get_limit(limit=pagination.per_page,
            #                                                  offset=(pagination.page - 1) * pagination.per_page)
            return await HotelsRepository(session).get_limit(per_page=pagination.per_page,
                                                             page=pagination.page)


@router.get("/find",
            summary="Поиск отелей по заданным параметрам и "
                    "вывод итогового списка с разбивкой по страницам",
            )
async def find_hotels_get(pagination: PaginationPagesDep,
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
    ## Функция ищет отели по заданным параметрам и выводит информацию о найденных отелях с разбивкой по страницам.

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

    location_type = '' if starts_with else '%'
    get_hotels_query = select(HotelsORM)

    if not (hotel_location or hotel_title):
        return "Не заданы параметры для выбора отеля"

    if hotel_location:
        if case_sensitivity:
            get_hotels_query = (get_hotels_query
                                .where(HotelsORM.location.like(location_type + hotel_location + "%"))
                                )
        else:
            get_hotels_query = (get_hotels_query
                                .where(HotelsORM.location.ilike(location_type + hotel_location + "%"))
                                )

    if hotel_title:
        if case_sensitivity:
            get_hotels_query = (get_hotels_query
                                .filter(HotelsORM.title.like(location_type + hotel_title + "%"))
                                )
        else:
            get_hotels_query = (get_hotels_query
                                .filter(HotelsORM.title.ilike(location_type + hotel_title + "%"))
                                )

    get_hotels_query = get_hotels_query.order_by(HotelsORM.id)

    skip = (pagination.page - 1) * pagination.per_page
    get_hotels_query = (get_hotels_query
                        .limit(pagination.per_page)
                        .offset(skip)
                        )

    async with async_session_maker() as session:
        # result = await session.execute(get_hotels_query)
        return await HotelsRepository(session).get_limit(query=get_hotels_query,
                                                         per_page=pagination.per_page,
                                                         page=pagination.page)
    # # hotels_lst = result.scalars().all()
    # hotels_lst = result
    #
    # status = (f"Страница {pagination.page}, установлено отображение {pagination.per_page} "
    #           f"элемент(-а/-ов) на странице.",
    #           f"Всего выводится {len(hotels_lst)} элемент(-а/-ов) на странице.")
    # if len(hotels_lst) == 0:
    #     status = (status, f"Данные отсутствуют.")
    # else:
    #     status = (status, hotels_lst)
    #
    # return status


@router.get("/{hotel_id}",
            summary="Получение из базы данных выбранной записи по идентификатору отеля",
            )
async def get_hotel_id_get(hotel_path: Annotated[HotelPath, Path()]):
    """
    ## Функция получает из базы данных выбранную запись по идентификатору отеля.

    Параметры (передаются в URL):
    - ***:param** id:* Идентификатор отеля (обязательно).

    ***:return:*** Словарь: `{"status": str, "err_type": int, "got row": dict}`, где:

    - ***status***: Текстовое описание результата операции.;
    - ***err_type***: Код результата операции.
      Принимает значения:
      - 0 (OK: выполнено нормально, без ошибок).
      - 1 (Error: Для объекта с указанным идентификатором ничего не найдено).
      - 2 (Error: Не указан идентификатор отеля для выборки).
    - ***got_row***: Выбранный объект. Выводятся в виде словаря элементы
      объекта HotelsORM.
    """

    async with async_session_maker() as session:
        #     # Получаем объект по первичному ключу
        #     hotel = await session.get(HotelsORM, hotel_path.hotel_id)
        #
        #     # если не найден, отправляем статусный код и сообщение об ошибке
        #     if not hotel:
        #         return {"status": "Error",
        #                 "deleted": f"Не найден отель с идентификатором {hotel_path.hotel_id}."}
        #     await session.delete(hotel)  # Удаляем объект
        #     await session.commit()  # Подтверждаем удаление
        #     deleted = {"id": hotel.id,
        #                "title": hotel.title,
        #                "location": hotel.location, }
        #
        # return {"status": "OK", "deleted": deleted}

        # Применяется метод session.get
        # Возвращает None или объект
        result = await HotelsRepository(session).get_id(object_id=hotel_path.hotel_id)
        # Применяется метод select и затем result.scalars().one_or_none()
        # Так как ищем по ключу, то элемент один или его нет.
        # result = await HotelsRepository(session).get_one_or_none(id=hotel_path.hotel_id)
        # await session.commit()  # Подтверждаем изменение
    #     # return {"status": status, "err_type": err_type}
    return result


@router.delete("/{hotel_id}",
               summary="Удаление выбранной записи по идентификатору отеля",
               )
async def delete_hotel_id_del(hotel_path: Annotated[HotelPath, Path()]):
    """
    ## Функция удаляет выбранную запись.

    Параметры (передаются в URL):
    - ***:param** id:* Идентификатор отеля (обязательно).

    ***:return:*** Словарь: `{"status": str, "deleted": str | dict}`, где:

    - ***status***: статус операции (реализованы варианты: OK и Error);
    - ***deleted***: это список выводимых отелей в формате:
    `list(dict("id": hotel.id, "title": hotel.title, "location": hotel.location))`
    или информационная строка.

    В текущей реализации статус завершения операции всегда один и тот же: OK

    Если работать с БД, то добавятся новые статусы.
    """

    async with async_session_maker() as session:
        #     # Получаем объект по первичному ключу
        #     hotel = await session.get(HotelsORM, hotel_path.hotel_id)
        #
        #     # если не найден, отправляем статусный код и сообщение об ошибке
        #     if not hotel:
        #         return {"status": "Error",
        #                 "deleted": f"Не найден отель с идентификатором {hotel_path.hotel_id}."}
        #     await session.delete(hotel)  # Удаляем объект
        #     await session.commit()  # Подтверждаем удаление
        #     deleted = {"id": hotel.id,
        #                "title": hotel.title,
        #                "location": hotel.location, }
        #
        # return {"status": "OK", "deleted": deleted}
        result = await HotelsRepository(session).delete(id=hotel_path.hotel_id)
        await session.commit()  # Подтверждаем изменение
    #     # return {"status": status, "err_type": err_type}
    # result: {"status": status, "err_type": err_type, "deleted rows": result}
    if result["deleted rows"] is None:
        result["status"] = f"Для отеля с идентификатором {hotel_path.hotel_id} ничего не найдено"
    return result


@router.delete("",
               summary="Удаление выбранных записей с выборкой по наименованию "
                       "и адресу отеля - что требуется удалять",
               )
async def delete_hotel_param_del(hotel_location: Annotated[str | None, Query(min_length=3,
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

    Параметры (передаются методом Query):
    - ***:param** hotel_location:* Адрес отеля (может отсутствовать).
    - ***:param** hotel_title:* Название отеля (может отсутствовать).
    - ***:param** case_sensitivity:* Поиск с учётом регистра (True) или
         регистронезависимый (False или None). Может отсутствовать.
    - ***:param** starts_with:* Поиск строк, начинающихся с заданного
         текста (True), или поиск строк, содержащих заданный текст
         (False или None). Может отсутствовать.

    ***:return:*** Словарь: `{"status": str, "deleted method": str, "deleted": str | dict}`, где:

    - ***status***: статус операции (реализованы варианты: OK и Error);
    - ***deleted***: это список выводимых отелей в формате:
    `list(dict("id": hotel.id, "title": hotel.title, "location": hotel.location))`
    или информационная строка.

    Один из двух параметров `hotel_location` или `hotel_title` обязан быть задан.

    Значения `case_sensitivity` и `starts_with` влияют на поиск по обоим
    параметрам `hotel_location` и `hotel_title`.

    Если переданы оба параметра `hotel_location` и `hotel_title`, то
    выбираться будет отель, соответствующий обоим параметрам одновременно.

    """

    location_type = '' if starts_with else '%'
    delete_hotels_stmt = delete(HotelsORM)

    if not (hotel_location or hotel_title):
        return {"status": "Error",
                "deleted method": "Ничего не удалялось",
                "deleted": "Не заданы параметры для выбора отеля"}

    if hotel_location:
        if case_sensitivity:
            delete_hotels_stmt = (delete_hotels_stmt
                                  .where(HotelsORM.location.like(location_type + hotel_location + "%"))
                                  )
        else:
            delete_hotels_stmt = (delete_hotels_stmt
                                  .where(HotelsORM.location.ilike(location_type + hotel_location + "%"))
                                  )

    if hotel_title:
        if case_sensitivity:
            delete_hotels_stmt = (delete_hotels_stmt
                                  .filter(HotelsORM.title.like(location_type + hotel_title + "%"))
                                  )
        else:
            delete_hotels_stmt = (delete_hotels_stmt
                                  .filter(HotelsORM.title.ilike(location_type + hotel_title + "%"))
                                  )

    # Подготовлены переменные:
    # get_hotels_query - запрос на выборку элементов
    #     SELECT hotels.id, hotels.title, hotels.location
    #     FROM hotels
    #     WHERE hotels.location ILIKE '%search_text%' AND hotels.title ILIKE '%search_text%' ORDER BY hotels.id

    async with async_session_maker() as session:
        # result = await session.execute(delete_hotels_stmt)
        # hotels_to_delete_lst = result.scalars().all()
        result = await HotelsRepository(session).delete(delete_stmt=delete_hotels_stmt)

        # # если не найден, отправляем статусный код и сообщение об ошибке
        # if not hotels_to_delete_lst:
        #     return {"status": "Error",
        #             "deleted method": "Ничего не удалялось",
        #             "deleted": "Отели с параметром поиска: "
        #                        f"местонахождение: {hotel_location}, "
        #                        f"наименование: {hotel_title} "
        #                        f"не найдены."}
        #
        # # Удалить поэлементно. Удаляем объекты в цикле.
        # for hotel in hotels_to_delete_lst:
        #     await session.delete(hotel)
        await session.commit()  # Подтверждаем изменения

    # # Формируем список удалённых объектов
    # deleted = []
    # for hotel in hotels_to_delete_lst:
    #     deleted.append({"id": hotel.id,
    #                     "title": hotel.title,
    #                     "location": hotel.location, })
    #     # print(f"{hotel.id=}\n{hotel.title=}\n{hotel.location=}")
    # return {"status": "OK", "deleted": deleted}

    # result: {"status": status, "err_type": err_type, "deleted rows": result}
    if result["deleted rows"] is None:
        # result["status"] = ("Отели с параметром поиска: "
        #                     f"местонахождение: "
        #                     f"{if hotel_location is None}, "
        #                     f"наименование: {hotel_title} "
        #                     f"не найдены.")
        result["status"] = ("Не найдены отели с параметром поиска: местонахождение: " +
                            ("не задано" if hotel_location is None else f"{hotel_location}") +
                            ", наименование: " +
                            ("не задано" if hotel_title is None else f"{hotel_title}") +
                            ".")
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
             )
async def create_hotel_post(hotel_caption: Annotated[HotelDescriptionRecURL,
                                                     Body(openapi_examples=openapi_examples_dict)]):
    """
    ## Функция создаёт запись.

    Параметры (передаются методом Body):
    - ***:param** title:* Название отеля (обязательно)
    - ***:param** location:* Местонахождение отеля (обязательно)

    ***:return:*** Словарь: `dict("status": status, "added data": added_hotel)`, где
        - *status*: str. Статус завершения операции.
        - *added_hotel*: HotelPydanticSchema. Запись с добавленными данными.
          Тип возвращаемых элементов преобразован к указанной схеме Pydantic.

    В текущей реализации статус завершения операции всегда один и тот же: OK
    """
    async with async_session_maker() as session:
        # преобразуют модель в словарь Python: HotelDescriptionRecURL.model_dump()
        # Раскрываем (распаковываем) словарь в список именованных аргументов
        # "title"= , "location"=
        # add_hotel_stmt = insert(HotelsORM).values(**hotel_caption.model_dump())
        # result = await session.execute(add_hotel_stmt)
        # add_id = result.scalars().all()[0]
        result = await HotelsRepository(session).add(hotel_caption)
        await session.commit()
        status = "OK"
    return {"status": status, "added data": result}


@router.put("/{hotel_id}",
            summary="Обновление ВСЕХ данных одновременно для выбранной "
                    "записи, выборка происходит по идентификатору отеля",
            )
async def change_hotel_put(hotel_path: Annotated[HotelPath, Path()],
                           hotel_caption: Annotated[HotelDescriptionRecURL, Body()],
                           ):
    """
    ## Функция изменяет (обновляет) ВСЕ данные одновременно

    В ручке PUT мы обязаны передать оба параметра title и location.

    Параметры (передаются в URL):
    - ***:param** hotel_id:* Идентификатор отеля (обязательно).

    Параметры (передаются методом Body):
    - ***:param** title:* Название отеля (обязательно).
    - ***:param** location:* Адрес отеля (обязательно).

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


    Значение статуса завершения операции:
    - 0: все OK.
    - 1: ничего не найдено.
    """
    # status = f"Для отеля с идентификатором {hotel_path.hotel_id} ничего не найдено"
    # err_type = 1
    async with async_session_maker() as session:
        #     # Обновить сразу все найденные записи - обновление через метод update
        #     update_hotels_stmt = (update(HotelsORM)
        #                           .where(HotelsORM.id == hotel_path.hotel_id)
        #                           .values(title=hotel_caption.title,
        #                                   location=hotel_caption.location)
        #                           )
        #     result = await session.execute(update_hotels_stmt)
        #     updated_rows = result.rowcount
        #     if updated_rows == 0:
        #         return {"status": status, "err_type": err_type}
        #     await session.commit()  # Подтверждаем изменение
        # status = "OK"
        # err_type = 0
        # result = await HotelsRepository(session).edit(edited_data=hotel_caption,
        #                                               filtering={"id": hotel_path.hotel_id})
        result = await HotelsRepository(session).edit(edited_data=hotel_caption,
                                                      id=hotel_path.hotel_id)
        await session.commit()  # Подтверждаем изменение
    # return {"status": status, "err_type": err_type}
    return result


@router.patch("/{hotel_id}",
              summary="Обновление каких-либо данных выборочно или всех данных сразу "
                      "для выбранной записи, выборка происходит по идентификатору отеля",
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

    async with async_session_maker() as session:
        # Получаем объект по первичному ключу
        #     hotel = await session.get(HotelsORM, hotel_path.hotel_id)
        #
        #     # если не найден, отправляем статусный код и сообщение об ошибке
        #     if not hotel:
        #         return {"status": status, "err_type": err_type}
        #
        #     if hotel_caption.title:
        #         hotel.title = hotel_caption.title
        #     if hotel_caption.location:
        #         hotel.location = hotel_caption.location
        #     await session.commit()  # Подтверждаем изменение
        # err_type = 0
        # status = "OK"

        # result = await HotelsRepository(session).edit(edited_data=hotel_caption,
        #                                               exclude_unset=True,
        #                                               id=hotel_path.hotel_id)
        result = await HotelsRepository(session).edit_id(edited_data=hotel_caption,
                                                         exclude_unset=True,
                                                         object_id=hotel_path.hotel_id)
        await session.commit()  # Подтверждаем изменение
    # return {"status": status, "err_type": err_type}
    return result
