from fastapi import Query, Body, Path, APIRouter
from typing import Annotated
# from schemas.hotels import HotelPath, HotelCaptionRec, HotelCaptionOpt
# from schemas.hotels import RoomPathTest, HotelQueryTest, HotelBodyTest
import schemas.hotels_examples as hotels_schms

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
       Функция: show_hotels_get
get
/hotels/{hotel_id} - Вывод информации об одном отеле
       Функция: hotel_get
       Параметры (передаются в URL):
       - Идентификатор отеля для вывода
         - hotel_id: int | None
       Параметры (передаются через Query-параметры методом Query):
       - Наименование title отеля для вывода
         - hotel_title: str | None

delete
/hotels/{hotel_id} - Удаление выбранной записи
       Функция: delete_hotel_del
       Параметры (передаются в URL):
       - Идентификатор удаляемого отеля
         - hotel_id: int

post
/hotels - Добавить данные
       Функция: create_hotel_post
       Параметры передаются через ТЕЛО запроса (метод Body):
         - Данные, которые надо добавить:
           - hotel_title: str
           - hotel_name: str
                 
put
/hotels/{hotel_id} - Обновление ВСЕХ данные одновременно
       Функция: hotel_put
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
       Функция: hotel_patch
       Параметры:
         - Индекс, для которого обновляются данные:
           - hotel_id: int
         - Данные, которые надо обновить:
           - hotel_title: str
           - hotel_name: str
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


# См. документацию про примеры:
# https://fastapi.tiangolo.com/ru/tutorial/schema-extra-example/?h=#body-with-multiple-examples
# https://fastapi.qubitpi.org/tutorial/schema-extra-example/?h=#body-with-multiple-examples

@router.put("/test/examples_items/{item_id}")
async def update_item_examples(
    *,
    item_id: int,
    item: Annotated[
        hotels_schms.ItemTest,
        Body(examples=[{"name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                        }
                       ],
             ),
    ],
):
    """
    Если используется Depends или дополнительные Query-параметры, то
    ломается (работает неправильно) использование схемы в Query().
    """
    results = {"item_id": item_id, "item": item}
    return results


@router.put("/test/openapi_examples_items/{item_id}")
async def update_item_openapi_examples(
    *,
    item_id: int,
    item: Annotated[
        hotels_schms.ItemTest,
        Body(openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        ),
    ],
):
    """
    Если используется Depends или дополнительные Query-параметры, то
    ломается (работает неправильно) использование схемы в Query().
    """
    results = {"item_id": item_id, "item": item}
    return results


@router.post("/test/{hotel_id}/{room_id}",
             summary="Тестовая ручка для проверки методов Path(), "
                     "Query(), Body() со схемами Pydantic",
             tags=["Отели"])
def hotel_test_post(room_path: Annotated[hotels_schms.RoomPathTest, Path()],
                    hotel_data_query: Annotated[hotels_schms.HotelQueryTest, Query()],
                    # hotel_data_body: Annotated[hotels_schms.HotelBodyTest, Body()],
                    # В параметре examples порядок полей при выводе такой, как указан в коде.
                    # Переопределяет параметр examples, если он задан в описании схемы.
                    # Если указать несколько значений, то пока они игнорируются, кроме первого:
                    # в документации указывается, что полный вывод всех данных пока не
                    # возможен по внешним причинам.
                    hotel_data_body: Annotated[hotels_schms.HotelBodyTest, Body(examples=[{"hotel_body_str": "Fwewwoo",
                                                                                          "hotel_body_int": 12,
                                                                                           },
                                                                                          ]
                                                                                )
                                               ],
                    ):
    """
    Если используется Depends или дополнительные Query-параметры, то
    ломается (работает неправильно) использование схемы в Query().
    """
    return (f"{room_path.hotel_id = }, {room_path.room_id = }",
            f"{room_path = }",
            f"{hotel_data_query = }",
            f"{hotel_data_body = }")


@router.post("/test/{hotel_id}/{room_id}-{room_number}",
             summary="Тестовая ручка для проверки методов Path(), "
                     "Query(), Body() со схемами Pydantic",
             tags=["Отели"])
def hotel_test_post(room_path: Annotated[hotels_schms.RoomPathTest, Path()],
                    hotel_data_query: Annotated[hotels_schms.HotelQueryTest, Query()],
                    hotel_data_body: Annotated[hotels_schms.HotelBodyTest, Body()],
                    ):
    """
    Если используется Depends или дополнительные Query-параметры, то
    ломается (работает неправильно) использование схемы в Query().
    """
    return (f"{room_path.hotel_id = }, {room_path.room_id = }, {room_path.room_number = }",
            f"{room_path = }",
            f"{hotel_data_query = }",
            f"{hotel_data_body = }")


@router.get("",
            tags=["Отели"],
            summary="Вывод списка всех отелей одновременно с "
                    "разбивкой по страницам или весь список полностью",
            )
# Если описать параметры, как в комменте ниже,
# то в API не будет пояснения, какой параметр что значит
# def show_hotels_get(page: int = 0, per_page: int = 10):
# alias="item-query" - позволяет в адресной строке можно указать варианты:
# - http://127.0.0.1:8000/items/?per_page=    это определяется параметром per_page
# - http://127.0.0.1:8000/items/?per-page=    это определяется alias="per-page"
def show_hotels_get(page: Annotated[int,
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
# Схема hotels_schms.HotelPath описана так:
# class HotelPath(BaseModel):
#     hotel_id: int = Field(description="Идентификатор отеля",
#                           ge=1,
#                           )
# Соответственно, вместо параметра:
# hotel_path: Annotated[hotels_schms.HotelPath, Path()],
# нельзя писать hotel_id: Annotated[hotels_schms.HotelPath, Path()],
# надеясь получить конструкцию вида: hotel_id.hotel_id.
# FastAPI это будет считать ошибкой и выдаст сообщение:
# AssertionError: Path params must be of one of the supported types.
# То есть, можно сделать так:
#   def hotel_get(hotel_path: int,
#   def hotel_get(hotel_path: Annotated[int, Path(description="Идентификатор отеля",
#                                                 ge=1,)],
#   def hotel_get(hotel_path: Annotated[hotels_schms.HotelPath, Path()],
def hotel_get(hotel_path: Annotated[hotels_schms.HotelPath, Path()],
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
    if not (hotel_path.hotel_id or hotel_title):
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
        if hotel_path.hotel_id and hotel["id"] != hotel_path.hotel_id:
            continue
        if hotel_title and hotel["title"] != hotel_title:
            continue
        found_hotel.append(hotel)
    return found_hotel


@router.delete("/{hotel_id}",
               tags=["Отели"],
               summary="Удаление выбранной записи",
               )
def delete_hotel_del(hotel_path: Annotated[hotels_schms.HotelPath, Path()]):
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
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_path.hotel_id]
    return {"status": "OK"}


@router.post("",
             tags=["Отели"],
             summary="Создание записи с новым отелем",
             )
def create_hotel_post(hotel_caption: Annotated[hotels_schms.HotelCaptionRec, Body()]):
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
                   "title": hotel_caption.hotel_title,
                   "name": hotel_caption.hotel_name
                   })
    return {"status": status}


@router.put("/{hotel_id}",
            tags=["Отели"],
            summary="Обновление ВСЕХ данные одновременно",
            )
def hotel_put(hotel_path: Annotated[hotels_schms.HotelPath, Path()],
              hotel_caption: Annotated[hotels_schms.HotelCaptionRec, Body()]
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

    status = f"With {hotel_path.hotel_id:} nothing was found"
    err_type = 1

    # Если работать с БД, то изменение данных об отеле надо оформить блоком TRY.
    for item in hotels:
        if item["id"] == hotel_path.hotel_id:
            item["title"] = hotel_caption.hotel_title
            item["name"] = hotel_caption.hotel_name
            status = "OK"
            err_type = 0
            break
    return {"status": status, "err_type": err_type}


@router.patch("/{hotel_id}",
              tags=["Отели"],
              summary="Обновление каких-либо данных выборочно или всех данных сразу",
              )
# def hotel_id_patch(hotel_id: int = Path(description="Идентификатор отеля"),
#                    hotel_title: str | None = Body(default=None),
#                    hotel_name: str | None = Body(default=None)
#                    ):
def hotel_patch(hotel_path: Annotated[hotels_schms.HotelPath, Path()],
                hotel_caption: Annotated[hotels_schms.HotelCaptionOpt, Body()],
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

    status = f"With {hotel_path.hotel_id:} nothing was found"
    err_type = 1

    # Если работать с БД, то изменение данных об отеле надо оформить блоком TRY.
    for item in hotels:
        if item["id"] == hotel_path.hotel_id:
            if hotel_caption.hotel_title:
                item["title"] = hotel_caption.hotel_title
            if hotel_caption.hotel_name:
                item["name"] = hotel_caption.hotel_name
            status = "OK"
            err_type = 0
            break
    return {"status": status, "err_type": err_type}
