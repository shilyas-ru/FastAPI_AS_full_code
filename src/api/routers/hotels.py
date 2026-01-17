from fastapi import Query, Body, Path, APIRouter
from typing import Annotated
from src.schemas.hotels import HotelPath, HotelCaptionRec, HotelCaptionOpt
# import schemas.hotels as hotels_schms

from src.api.dependencies.dependencies import PaginationPagesDep, PaginationAllDep

"""
Данные передаются через URL, через Query-параметры (метод Query)
или через ТЕЛО запроса (метод Body).

Реализованы два варианта для put и patch - когда параметр hotel_id
- передаётся в URL;
- передаётся через ТЕЛО запроса (метод Body).

Рабочие ссылки (список методов, параметры в подробном перечне):
get("/hotels") - Вывод списка всех отелей с разбивкой по страницам или всего списка полностью
get("/hotels/find") - Поиск отелей по заданным параметрам и вывод итогового списка с разбивкой по страницам
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
/hotels/find - Вывод информации об одном отеле
       Функция: find_hotels_get
       Параметры (передаются через Query-параметры методом Query):
       - Идентификатор отеля для вывода
         - hotel_id: int | None
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
       Функция: change_hotel_put
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
       Функция: change_hotel_patch
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


# @router.post("/test/{hotel_id}/{room_id}-{room_number}",
#              summary="Тестовая ручка для проверки методов Path(), "
#                      "Query(), Body() со схемами Pydantic",
#              tags=["Отели"])
# def hotel_test_post(room_path: Annotated[hotels_schms.RoomPathTest, Path()],
#                     hotel_data_query: Annotated[hotels_schms.HotelQueryTest, Query()],
#                     hotel_data_body: Annotated[hotels_schms.HotelBodyTest, Body()],
#                     # В параметре examples порядок полей при выводе такой, как указан в коде.
#                     # Переопределяет параметр examples, если он задан в описании схемы.
#                     # Если указать несколько значений, то пока они игнорируются, кроме первого:
#                     # в документации указывается, что полный вывод всех данных пока не
#                     # возможен по внешним причинам.
#                     # hotel_data_body: Annotated[hotels_schms.HotelBodyTest,
#                     #                            Body(examples=[{"hotel_body_str": "Fwewwoo",
#                     #                                            "hotel_body_int": 12,
#                     #                                            },
#                     #                                           ]
#                     #                                 )
#                     #                            ],
#                     ):
#     return (f"{room_path.hotel_id = }, {room_path.room_id = }",
#             f"{room_path = }",
#             f"{hotel_data_query = }",
#             f"{hotel_data_body = }")


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
def show_hotels_get(pagination: PaginationAllDep,
                    # page: Annotated[int,
                    #                 Query(ge=1,
                    #                       description="Номер страницы для вывода",
                    #                       )] = 1,
                    # per_page: Annotated[int,
                    #                     Query(ge=1,
                    #                           alias="per-page",
                    #                           description="Количество элементов на странице",
                    #                           )] = 3,
                    # all_hotels: Annotated[bool,
                    #                       Query(alias="all-hotels",
                    #                             description="Отображать весь список отелей полностью",
                    #                             )] = False,
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
    if pagination.all_hotels:
        return "Полный список отелей.", hotels

    skip = (pagination.page-1) * pagination.per_page
    if len(hotels) < skip+1:
        return (f"страница {pagination.page}, отображается {pagination.per_page} " 
                "элементов на странице.",
                f"Данные отсутствуют.")
    return f"страница {pagination.page}, отображается {pagination.per_page} " \
           f"элементов на странице.", hotels[skip: skip + pagination.per_page]


@router.get("/find",
            tags=["Отели"],
            summary="Поиск отелей по заданным параметрам и "
                    "вывод итогового списка с разбивкой по страницам",
            )
def find_hotels_get(pagination: PaginationPagesDep,
                    hotel_id: Annotated[int | None, Query(description="Идентификатор отеля",
                                                          ge=1
                                                          )] = None,
                    hotel_title: Annotated[str | None, Query(min_length=3,
                                                             description="Название (title) отеля"
                                                             )] = None,
                    ):
    """
    ## Функция ищет отели по заданным параметрам и выводит информацию о найденных отелях с разбивкой по страницам.

    Параметры (передаются методом Query):
    - ***:param** hotel_id:* Идентификатор отеля (может отсутствовать).
    - ***:param** hotel_title:* title отеля (может отсутствовать).

    Поиск по параметру hotel_title - регистронезависимый, выбираются записи,
    в которых значение в БД начинается с заданной в hotel_title строки.

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
        # if hotel_title and hotel["title"] != hotel_title:
        # if hotel_title and not hotel["title"].startswith(hotel_title):
        if hotel_title and not hotel["title"].title().startswith(hotel_title.title()):
            continue
        found_hotel.append(hotel)

    # Простой вывод
    # if pagination.page and pagination.per_page:
    #     return found_hotel[pagination.per_page * (pagination.page - 1):][:pagination.per_page]
    # return found_hotel

    skip = (pagination.page-1) * pagination.per_page
    if len(found_hotel) < skip+1:
        return (f"страница {pagination.page}, отображается {pagination.per_page} " 
                "элементов на странице.",
                f"Данные отсутствуют.")
    return f"страница {pagination.page}, отображается {pagination.per_page} " \
           f"элементов на странице.", found_hotel[skip: skip + pagination.per_page]


@router.delete("/{hotel_id}",
               tags=["Отели"],
               summary="Удаление выбранной записи",
               )
def delete_hotel_del(hotel_path: Annotated[HotelPath, Path()]):
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
def create_hotel_post(hotel_caption: Annotated[HotelCaptionRec, Body()]):
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
def change_hotel_put(hotel_path: Annotated[HotelPath, Path()],
                     hotel_caption: Annotated[HotelCaptionRec, Body()]
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


# def hotel_id_patch(hotel_id: int = Path(description="Идентификатор отеля"),
#                    hotel_title: str | None = Body(default=None),
#                    hotel_name: str | None = Body(default=None)
#                    ):

@router.patch("/{hotel_id}",
              tags=["Отели"],
              summary="Обновление каких-либо данных выборочно или всех данных сразу",
              )
# Тут параметр examples переопределяет то, что в схеме
def change_hotel_patch(hotel_path: Annotated[HotelPath,
                                             Path(examples=[{
                                                             "hotel_id": 1
                                                             }
                                                            ]
                                                  )
                                             ],
                       hotel_caption: Annotated[HotelCaptionOpt,
                                                Body(examples=[{
                                                                "hotel_title": "title отеля",
                                                                "hotel_name": "name отеля",
                                                                },
                                                               ]
                                                     )
                                                ],
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
