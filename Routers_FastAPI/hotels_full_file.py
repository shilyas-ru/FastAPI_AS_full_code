from fastapi import Query, Body, Path, APIRouter
from typing import Annotated

"""
Данные передаются через URL, через Query-параметры (метод Query)
или через ТЕЛО запроса (метод Body).

Реализованы два варианта для put и patch - когда параметр hotel_id
- передаётся в URL;
- передаётся через ТЕЛО запроса (метод Body).

Рабочие ссылки (список методов, параметры в подробном перечне):
get("/hotels") - Вывод списка всех отелей с разбивкой по страницам или всего списка полностью
get("/hotels/{hotel_id}") - Вывод информации об одном отеле
delete("/hotels/{hotel_id}") - Удаление выбранной записи
post("/hotels") - Добавить данные
put("/hotels/{hotel_id}") - Обновление ВСЕХ данные одновременно
patch("/hotels/{hotel_id}") - Обновление каких-либо данных выборочно или всех данных сразу
"""

"""
Реализованы методы API:
get
/hotels - Вывод списка всех отелей с разбивкой по страницам или всего списка полностью
       Функция: show_hotels
get
/hotels/{hotel_id} - Вывод информации об одном отеле
       Функция: get_hotel
       Параметры (передаются в URL):
       - Идентификатор отеля для вывода
         - hotel_id: int | None
       Параметры (передаются через Query-параметры методом Query):
       - Наименование title отеля для вывода
         - hotel_title: str | None

delete
/hotels/{hotel_id} - Удаление выбранной записи
       Функция: delete_hotel
       Параметры (передаются в URL):
       - Идентификатор удаляемого отеля
         - hotel_id: int

post
/hotels - Добавить данные
       Функция: create_hotel
       Параметры передаются через ТЕЛО запроса (метод Body):
         - Данные, которые надо добавить:
           - hotel_title: str
           - hotel_name: str
                 
put
/hotels/{hotel_id} - Обновление ВСЕХ данные одновременно
       Функция: hotel_id_put
       Параметры (передаются в URL):
         - Индекс, для которого обновляются данные передаётся в адресной строке:
           - hotel_id: int
       Параметры передаются через ТЕЛО запроса (метод Body):
         - Данные, которые надо обновить:
           - hotel_title: str
           - hotel_name: str

patch
/hotel/{hotel_id} - Обновление каких-либо данных выборочно или всех данных сразу
       Данные передаются через ТЕЛО запроса (метод Body)
       Функция: hotel_id_patch
       Параметры:
         - Индекс, для которого обновляются данные:
           - hotel_id: int
         - Данные, которые надо обновить:
           - hotel_title: str
           - hotel_name: str
"""


"""
URL-адреса метаданных и документации
https://fastapi.tiangolo.com/ru/tutorial/metadata/
"""

router = APIRouter(prefix="/hotels", tags=["Отели"])

hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Dubai", "name": "dubai"},
    {"id": 3, "title": "Dubai333", "name": "dubai333"},
    {"id": 4, "title": "Dubai444", "name": "dubai444"},
    {"id": 5, "title": "Dubai555", "name": "dubai555"},
    {"id": 6, "title": "Dubai666", "name": "dubai666"},
]


@router.get("/test",
            summary='Тестовая ручка для проверки типа данных "str | None" - '
                    'для обязательного параметра и параметра по умолчанию',
            tags=["Отели"])
def hotel_test_get(query_required: Annotated[str | None,
                                             Query(description='Параметр обязательный, '
                                                               'тип данных "str | None"')],
                   query_optional: Annotated[str | None,
                                             Query(description='Факультативный параметр, '
                                                               'тип данных "str | None"')] = None):
    return f"{query_required = }, {query_optional = }"


@router.post("/test/{hotel_id}",
             summary="Тестовая ручка для проверки методов Path(), "
                     "Query(), Body() с параметрами по умолчанию",
             tags=["Отели"])
def hotel_test_post(hotel_path: Annotated[int | None,
                                          Path(description="Идентификатор отеля")] = 5,
                    hotel_title: Annotated[str | None,
                                           Query(description="Данные hotel title")] = "title",
                    hotel_name: Annotated[str | None,
                                          Query(description="Данные hotel name")] = "name",
                    hotel_body_str: Annotated[str | None,
                                              Body(description="Данные hotel body str")] = "str",
                    hotel_body_int: Annotated[int | None,
                                              Body(description="Данные hotel body int")] = 3
                    ):
    return f"{hotel_path = }, {hotel_title = }, {hotel_name = }, " \
           f"{hotel_body_str = }, {hotel_body_int = }"


@router.get("",
            tags=["Отели"],
            summary="Вывод списка всех отелей одновременно с "
                    "разбивкой по страницам или весь список полностью",
            )
# Если описать параметры, как в комменте ниже,
# то в API не будет пояснения, какой параметр что значит
# def show_hotels(page: int = 0, per_page: int = 10):
# alias="item-query" - позволяет в адресной строке можно указать варианты:
# - http://127.0.0.1:8000/items/?per_page=    это определяется параметром per_page
# - http://127.0.0.1:8000/items/?per-page=    это определяется alias="per-page"
def show_hotels(page: Annotated[int,
                                Query(ge=1,
                                      description="Номер страницы для вывода",
                                      )] = 1,
                per_page: Annotated[int,
                                    Query(ge=1,
                                          alias="per-page",
                                          description="Количество элементов на странице",
                                          )] = 3,
                all_hotels: Annotated[bool,
                                      Query(alias="all-hotels",
                                            description="Отображать весь список отелей полностью",
                                            )] = False,
                ):
    """
    ## Функция выводит список всех отелей с разбивкой по страницам или весь список полностью.

    Параметры (передаются методом Query):
    - ***:param** page:* Номер страницы для вывода (должно быть больше 0, по умолчанию значение 1).
    - ***:param** per_page:* Количество элементов на странице (должно быть больше 0, по умолчанию значение 3).
    - ***:param** all_hotels:* отображать все отели сразу (логическое значение).

    ***:return:*** Список отелей или строка с уведомлением, если список отель пуст.

    Если параметр all_hotels имеет значение True, то остальные
    параметры игнорируются и сразу выводится полный список.

    Список отелей выводится в виде: list[info: str, list[dict{hotel_item: HotelItem}], где:
    - ***info***, это информация, какая страница выводится и сколько элементов на странице;
    - ***list[dict{hotel_item: HotelItem}]***, это список выводимых отелей.
    """
    if all_hotels:
        return "Полный список отелей.", hotels

    skip = (page-1) * per_page
    if len(hotels) < skip+1:
        return f"страница {page}, отображается {per_page} элементов на странице./nДанные отсутствуют."
    return f"страница {page}, отображается {per_page} элементов на странице.", hotels[skip: skip+per_page]


@router.get("/{hotel_id}",
            tags=["Отели"],
            summary="Вывод информации об одном отеле",
            )
# def get_hotel(hotel_id: int,   # можно не указывать для path-параметра item_id Path(...)
def get_hotel(hotel_id: int = Path(description="Идентификатор отеля"),
              hotel_title: str | None = Query(None, description="Название (title) отеля"),
              ):
    """
    ## Функция выводит информацию о выбранном отеле.

    Параметры (передаются в URL):
    - ***:param** hotel_id:* Идентификатор отеля (обязательно).

    Параметры (передаются методом Query):
    - ***:param** hotel_title:* title отеля (может отсутствовать).

    Если переданы оба параметра, то выбираться будет отель,
    соответствующий обоим параметрам одновременно.

    Параметр hotel_id целесообразно использовать, если в базе
    имеется несколько записей с одинаковым значением hotel_title.

    ***:return:*** Информация (словарь) о найденном отеле или None, если отель не найден.
    """

    global hotels
    if not (hotel_id or hotel_title):
        return "Не заданы параметры для выбора отеля"
    # Если будет несколько отелей с одинаковым hotel_title, но разным hotel_id
    # (или наоборот, одинаковый hotel_id, но разный hotel_title - но этот вариант уже ошибка),
    # То тогда будет результат в виде списка.
    found_hotel = []
    for hotel in hotels:
        # При не заданном параметре он будет иметь значение, установленное по умолчанию: None.
        # Конструкция "if hotel_id and" - позволяет отсечь варианты, когда параметр не задан.
        # Если её не использовать, то всегда будет выполняться условие hotel["id"] != hotel_id,
        # и цикл будет переходить к следующей итерации, игнорируя проверку со вторым параметром.
        if hotel_id and hotel["id"] != hotel_id:
            continue
        if hotel_title and hotel["title"] != hotel_title:
            continue
        found_hotel.append(hotel)
    return found_hotel


@router.delete("/{hotel_id}",
               tags=["Отели"],
               summary="Удаление выбранной записи",
               )
def delete_hotel(hotel_id: int = Path(description="Идентификатор отеля")):
    """
    ## Функция удаляет выбранную запись.

    Параметры (передаются в URL):
    - ***:param** hotel_id:* Идентификатор отеля (обязательно).

    ***:return:*** Статус завершения операции

    В текущей реализации статус завершения операции всегда один и тот же: OK

    Если работать с БД, то добавятся новые статусы.
    """
    global hotels

    # Если работать с БД, то удаление данных об отеле надо оформить блоком TRY.
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"status": "OK"}


@router.post("",
             tags=["Отели"])
def create_hotel(hotel_title: str = Body(),
                 hotel_name: str = Body(),
                 ):
    """
    ## Функция создаёт запись.

    Параметры (передаются методом Body):
    - ***:param** hotel_title:* title отеля (обязательно)
    - ***:param** hotel_name:* name отеля (обязательно)

    ***:return:*** Статус завершения операции.

    В текущей реализации статус завершения операции всегда один и тот же: OK

    Если работать с БД, то добавятся новые статусы.
    """
    global hotels

    status = "OK"
    # Если работать с БД, то добавление отеля надо оформить блоком TRY.
    hotels.append({"id": hotels[-1]["id"] + 1,
                   "title": hotel_title,
                   "name": hotel_name
                   })
    return {"status": status}


@router.put("/{hotel_id}",
            tags=["Отели"],
            summary="Обновление ВСЕХ данные одновременно",
            )
def hotel_id_put(hotel_id: int = Path(description="Идентификатор отеля"),
                 hotel_title: str = Body(),
                 hotel_name: str = Body()
                 ):
    """
    ## Функция изменяет (обновляет) ВСЕ данные одновременно

    В ручке PUT мы обязаны передать оба параметра title и name.

    Параметры (передаются в URL):
    - ***:param** hotel_id:* Идентификатор отеля (обязательно).

    Параметры (передаются методом Body):
    - ***:param** hotel_title:* title отеля (обязательно). Передаётся методом Body.
    - ***:param** hotel_name:* name отеля (обязательно). Передаётся методом Body.

    ***:return:*** Статус завершения операции (текст) и значение статуса операции (число): 0, 1

    Значение статуса завершения операции:
    - 0: все OK.
    - 1: ничего не найдено.
    """
    global hotels

    status = f"With {hotel_id:} nothing was found"
    err_type = 1

    # Если работать с БД, то изменение данных об отеле надо оформить блоком TRY.
    for item in hotels:
        if item["id"] == hotel_id:
            item["title"] = hotel_title
            item["name"] = hotel_name
            status = "OK"
            err_type = 0
            break
    return {"status": status, "err_type": err_type}


@router.patch("/{hotel_id}",
              tags=["Отели"],
              summary="Обновление каких-либо данных выборочно или всех данных сразу",
              )
def hotel_id_patch(hotel_id: int = Path(description="Идентификатор отеля"),
                   hotel_title: str | None = Body(default=None),
                   hotel_name: str | None = Body(default=None)
                   ):
    """
    ## Функция обновляет каких-либо данные выборочно или все данных сразу

    В PATCH ручке можем передать либо только title, либо только name,
    либо оба параметра сразу (тогда PATCH ничем не отличается от PUT ручки).

    Параметры (передаются в URL):
    - ***:param** hotel_id:* Идентификатор отеля (обязательно).

    Параметры (передаются методом Body):
    - ***:param** hotel_title:* title отеля (необязательно, не указан - изменяться не будет).
    - ***:param** hotel_name:* name отеля (необязательно, не указан - изменяться не будет).

    ***:return:*** Статус завершения операции (текст) и значение статуса операции (число): 0, 1

    Значение статуса завершения операции:
    - 0: все OK.
    - 1: ничего не найдено.
    """

    global hotels

    status = f"With {hotel_id:} nothing was found"
    err_type = 1

    # Если работать с БД, то изменение данных об отеле надо оформить блоком TRY.
    for item in hotels:
        if item["id"] == hotel_id:
            if hotel_title:
                item["title"] = hotel_title
            if hotel_name:
                item["name"] = hotel_name
            status = "OK"
            err_type = 0
            break
    return {"status": status, "err_type": err_type}
