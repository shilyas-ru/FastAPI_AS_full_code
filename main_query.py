# Задание №1: PUT и PATCH ручки отелей
# Необходимо реализовать 2 ручки:
#
#     Ручка PUT на изменение отеля
#     Ручка PATCH на изменения отеля
#
#
# Обе ручки позволяют видоизменить конкретный отель.
# Однако, в ручке PUT мы обязаны передать оба параметра
# title и name, а в PATCH ручке можем передать либо только title,
# либо только name, либо оба параметра сразу (тогда PATCH ничем
# не отличается от PUT ручки).
#
# Как будут выглядеть ручки:
#
# @app.put("/hotels/{hotel_id}")
# def ...
#
# @app.patch("/hotels/{hotel_id}")
# def ...

import uvicorn
from fastapi import FastAPI, Query

from pydantic import BaseModel


# Данные передаются через URL или через Query-параметры (метод Query).

# Реализованы два варианта для put и patch - когда параметр hotel_id
# - передаётся в URL;
# - передаётся в списке параметров методом Query.

# Рабочие ссылки (список методов, параметры в подробном перечне):
# get("/hotels") - Вывод списка всех отелей одновременно
# get("/hotel") - Вывод информации об одном отеле
# delete("/hotels/{hotel_id}") - Удаление выбранной записи
# post("/hotel") - Добавить данные
# put("/hotels/{hotel_id}") - Обновление ВСЕХ данные одновременно
#                   Параметр hotel_id передаётся в URL.
# put("/hotel") - Обновление ВСЕХ данные одновременно
#                   Параметр hotel_id передаётся в списке параметров методом Query.
# patch("/hotels/{hotel_id}") - Обновление каких-либо данных выборочно или всех данных сразу.
#                   Параметр hotel_id передаётся в URL.
# patch("/hotel") - Обновление каких-либо данных выборочно или всех данных сразу
#                   Параметр hotel_id передаётся в списке параметров методом Query.

# Реализованы методы API:
# get
# /hotels - Вывод списка всех отелей одновременно
#        Функция: show_hotels
# get
# /hotel - Вывод информации об одном отеле
#        Данные передаются через Query-параметры (метод Query)
#        Функция: get_hotel
#        Параметры:
#        - hotel_id: int | None
#        - hotel_title: str | None

# delete
# /hotels/{hotel_id} - Удаление выбранной записи
#        Данные передаются через Query-параметры (метод Query)
#        Функция: delete_hotel
#        Параметры:
#        - hotel_id: int

# post
# /hotel - Добавить данные
#        Данные передаются через Query-параметры (метод Query)
#        Функция: create_hotel
#        Параметры:
#        - title: str

# put
# /hotels/{hotel_id} - Обновление ВСЕХ данные одновременно
#        Данные передаются через Query-параметры (метод Query)
#        Индекс, для которого обновляются данные передаётся в адресной строке:
#        - hotel_id: int
#        Функция: hotel_id_put
#        Параметры:
#          Данные, которые надо обновить:
#        - hotel_title: str
#        - hotel_name: str

# put
# /hotel - Обновление ВСЕХ данные одновременно
#        Данные передаются через Query-параметры (метод Query)
#        Функция: hotel_put
#        Параметры:
#          Индекс, для которого обновляются данные:
#        - hotel_id: int
#          Данные, которые надо обновить:
#        - hotel_title: str
#        - hotel_name: str

# patch
# /hotel/{hotel_id} - Обновление каких-либо данных выборочно или всех данных сразу
#        Данные передаются через Query-параметры (метод Query)
#        Функция: hotel_id_patch
#        Параметры:
#          Индекс, для которого обновляются данные:
#        - hotel_id: int
#          Данные, которые надо обновить:
#        - hotel_title: str
#        - hotel_name: str

# patch
# /hotel- Обновление каких-либо данных выборочно или всех данных сразу
#        Данные передаются через Query-параметры (метод Query)
#        Индекс, для которого обновляются данные передаётся в адресной строке:
#        - hotel_id: int
#        Функция: hotel_patch
#        Параметры:
#          Данные, которые надо обновить:
#        - hotel_title: str
#        - hotel_name: str


app = FastAPI()

hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Dubai", "name": "dubai"},
]


class HotelItem(BaseModel):
    id: int
    title: str | None = None
    name: str | None = None


@app.get("/hotels",
         summary="Вывод списка всех отелей одновременно",
         description="<h2>Функция выводит список всех отелей.</h2>"
                     "Параметры отсутствуют"
         )
def show_hotels():
    return hotels


@app.get("/hotel",
         summary="Вывод информации об одном отеле",
         description="<h2>Функция выводит информацию о выбранном отеле.</h2>"
                     "<ul>Параметры (передаются методом Query):"
                     "<li>:<b><u>param</b></u> <i>hotel_id</i>: "
                     "Идентификатор отеля (может отсутствовать).</li>"
                     "<li>:<b><u>param</b></u> <i>hotel_title</i>: "
                     "title отеля (может отсутствовать).</li>"
                     "</ul>"
                     "<p>Если переданы оба параметра, то выбираться будет "
                     "отель, соответствующий обоим параметрам одновременно.</p>"
         )
def get_hotel(hotel_id: int | None = Query(None, description="Айдишник"),
              hotel_title: str | None = Query(None, description="Название отеля"),
              ):
    """
    Вывод информации об одном отеле по идентификатору и по title.
    :param hotel_id:  Идентификатор отеля (может отсутствовать).
    :param hotel_title: title отеля (может отсутствовать).
    :return: Информация (словарь) о найденном отеле или None, если отель не найден.
    """
    global hotels
    if not (hotel_id or hotel_title):
        return "Не заданы параметры для выбора отеля"
    # Если будет несколько отелей с одинаковым hotel_title, но разным hotel_id
    # (или наоборот, одинаковый hotel_id, но разный hotel_title - но этот вариант уже ошибка),
    # То тогда будет результат в виде списка.
    found_hotel = []
    for hotel in hotels:
        if hotel_id and hotel["id"] != hotel_id:
            continue
        if hotel_title and hotel["title"] != hotel_title:
            continue
        found_hotel.append(hotel)
    return found_hotel


@app.delete("/hotels/{hotel_id}",
            summary="Удаление выбранной записи",
            )
def delete_hotel(hotel_id: int):
    """
    ## Функция удаляет выбранную запись.

    Параметры (передаются в URL):
    - ***:param** hotel_id:* Идентификатор отеля (обязательно).

    ***:return:*** Статус завершения операции
    """
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"status": "OK"}


@app.post("/hotel")
def create_hotel(hotel_title: str = Query(description="Название title"),
                 hotel_name: str = Query(description="Название name"),
                 ):
    """
    ## Функция создаёт запись.

    Параметры (передаются методом Query):
    - ***:param** hotel_title:* title отеля (обязательно)
    - ***:param** hotel_name:* name отеля (обязательно)

    ***:return:*** Статус завершения операции
    """
    global hotels

    hotels.append({"id": hotels[-1]["id"] + 1,
                   "title": hotel_title,
                   "name": hotel_name
                   })
    return {"status": "OK"}


def hotel_change_all(hotel_id, hotel_title, hotel_name):
    """
    Обновление ВСЕХ данные одновременно
    Обязаны передать все параметры - id, title и name.

    Параметры:
    - :param hotel_id: Идентификатор отеля (обязательно)
    - :param hotel_title: title отеля (обязательно)
    - :param hotel_name: name отеля (обязательно)

    ***:return:*** Статус завершения операции (текст) и тип ошибки (0: все OK, 1,2 - ошибка)
    """
    global hotels

    if hotel_id and hotel_title and hotel_name:
        # Данные переданы полностью, предполагаем, что по id м.б. отель не будет найден.
        status = f"With {hotel_id:} nothing was found"
        err_type = 1
    else:
        status = "Данные переданы не полностью"
        err_type = 2

    for item in hotels:
        if item["id"] == hotel_id:
            item["title"] = hotel_title
            item["name"] = hotel_name
            status = "OK"
            err_type = 0
            break
    return {"status": status, "err_type": err_type}


@app.put("/hotel",
         summary="Обновление ВСЕХ данные одновременно",
         )
def hotel_put(hotel_id: int = Query(description="Айдишник"),
              hotel_title: str = Query(description="Название title"),
              hotel_name: str = Query(description="Название name")
              ):
    """
    ## Функция изменяет (обновляет) ВСЕ данные одновременно

    В ручке PUT мы обязаны передать оба параметра title и name.

    Параметры (передаются методом Query):
    - ***:param** hotel_id:* Идентификатор отеля (обязательно)
    - ***:param** hotel_title:* title отеля (обязательно)
    - ***:param** hotel_name:* name отеля (обязательно)

    ***:return:*** Статус завершения операции (текст) и тип ошибки (0: все OK, 1,2 - ошибка)
    """
    return hotel_change_all(hotel_id, hotel_title, hotel_name)


@app.put("/hotels/{hotel_id}",
         summary="Обновление ВСЕХ данные одновременно",
         )
def hotel_id_put(hotel_id: int,
                 hotel_title: str = Query(description="Название title"),
                 hotel_name: str = Query(description="Название name")
                 ):
    """
    ## Функция изменяет (обновляет) ВСЕ данные одновременно

    В ручке PUT мы обязаны передать оба параметра title и name.

    Параметры:
    - ***:param** hotel_id:* Идентификатор отеля. Передаётся в URL.
    - ***:param** hotel_title:* title отеля (обязательно). Передаётся методом Query.
    - ***:param** hotel_name:* name отеля (обязательно). Передаётся методом Query.

    ***:return:*** Статус завершения операции (текст) и тип ошибки (0: все OK, 1,2 - ошибка)
    """
    return hotel_change_all(hotel_id, hotel_title, hotel_name)


def hotel_change(hotel_id, hotel_title, hotel_name):
    """
    Обновление каких-либо данных выборочно или всех данных сразу

    Параметры:
    - :param hotel_id: Идентификатор отеля (обязательно)
    - :param hotel_title: title отеля (может отсутствовать)
    - :param hotel_name: name отеля (может отсутствовать)

    ***:return:*** Статус завершения операции (текст) и тип ошибки (0: все OK, 1,2 - ошибка)
    """
    global hotels

    if hotel_id:
        # Данные переданы полностью, предполагаем, что по id м.б. отель не будет найден.
        status = f"With {hotel_id:} nothing was found"
        err_type = 1
    else:
        status = "Не передан идентификатор отеля"
        err_type = 2

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


@app.patch("/hotel",
           summary="Обновление каких-либо данных выборочно или всех данных сразу",
           description="<h1>Пояснение по hotel_patch</h2>"
                       "<p>В PATCH ручке можем передать либо только title, "
                       "либо только name, либо оба параметра сразу "
                       "(тогда PATCH ничем не отличается от PUT ручки)</p>"
                       "<ul>Параметры (передаются методом Query):"
                       "<li><b><i>:param</b> hotel_id:</i> Идентификатор отеля (обязательно)</li>"
                       "<li><b><i>:param</b> hotel_title:</i> title отеля (не обязательно, "
                       "не указан - изменяться не будет)</li>"
                       "<li><b><i>:param</b> hotel_name:</i> name отеля (не обязательно, "
                       "не указан - изменяться не будет)</li>"
                       "</ul>"
                       "<p><b><i>:return:</b></i> Статус завершения операции</p>"
           )
def hotel_patch(hotel_id: int | None = Query(None, description="Айдишник"),
                hotel_title: str | None = Query(None, description="Название title"),
                hotel_name: str | None = Query(None, description="Название name")
                ):
    """
    Обновление каких-либо данных выборочно или всех данных сразу

    :param hotel_id: Идентификатор отеля (обязательно)
    :param hotel_title: title отеля (необязательно, не указан - изменяться не будет)
    :param hotel_name: name отеля (необязательно, не указан - изменяться не будет)
    :return: Статус завершения операции
    """
    return hotel_change_all(hotel_id, hotel_title, hotel_name)


@app.patch("/hotels/{hotel_id}",
           summary="Обновление каких-либо данных выборочно или всех данных сразу",
           description="<h1>Пояснение по hotel_patch</h2>"
                       "<p>В PATCH ручке можем передать либо только title, "
                       "либо только name, либо оба параметра сразу "
                       "(тогда PATCH ничем не отличается от PUT ручки)</p>"
                       "<ul>"
                       "<li><b><i>:param</b> hotel_id:</i> Идентификатор отеля (обязательно)</li>"
                       "<li><b><i>:param</b> hotel_title:</i> title отеля (не обязательно, "
                       "не указан - изменяться не будет)</li>"
                       "<li><b><i>:param</b> hotel_name:</i> name отеля (не обязательно, "
                       "не указан - изменяться не будет)</li>"
                       "</ul>"
                       "<p><b><i>:return:</b></i> Статус завершения операции</p>"
           )
def hotel_id_patch(hotel_id: int,
                   hotel_title: str | None = Query(None, description="Название title"),
                   hotel_name: str | None = Query(None, description="Название name")
                   ):
    """
    Обновление каких-либо данных выборочно или всех данных сразу

    :param hotel_id: Идентификатор отеля (обязательно)
    :param hotel_title: title отеля (необязательно, не указан - изменяться не будет)
    :param hotel_name: name отеля (необязательно, не указан - изменяться не будет)
    :return: Статус завершения операции
    """
    return hotel_change_all(hotel_id, hotel_title, hotel_name)


if __name__ == "__main__":
    uvicorn.run("main_query:app", host="127.0.0.1", port=8000, reload=True)
