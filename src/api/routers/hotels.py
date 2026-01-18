from fastapi import Query, Body, Path, APIRouter
from typing import Annotated

from src.models.hotels import HotelsORM
from src.schemas.hotels import HotelPath, HotelCaptionRec, HotelCaptionOpt
# import schemas.hotels as hotels_schms

from src.api.dependencies.dependencies import PaginationPagesDep, PaginationAllDep
from src.database import async_session_maker, engine
from sqlalchemy import insert  # Для реализации SQL команды INSERT
from sqlalchemy import select  # Для реализации SQL команды SELECT
from sqlalchemy import delete  # Для реализации SQL команды DELETE
from sqlalchemy import update  # Для реализации SQL команды UPDATE

"""
Рабочие ссылки (список методов, параметры в подробном перечне):
get("/hotels") - Вывод списка всех отелей с разбивкой по страницам или всего списка полностью.
        Функция: show_hotels_get
get("/hotels/find") - Поиск отелей по заданным параметрам и вывод итогового списка с 
        разбивкой по страницам.
        Функция: find_hotels_get
        Для поиска реализованы возможности:
          - искать с учётом регистра или не учитывая регистр букв;
          - искать строки, начинающиеся на заданное значение или искать строки, содержащие заданное значение.
delete("/hotels/{hotel_id}") - Удаление выбранной записи по идентификатору отеля.
        Функция: delete_hotel_id_del
delete("/hotels") - Удаление выбранных записей с выборкой, что удалять, по наименованию 
        и адресу отеля.
        Функция: delete_hotel_param_del
        Для выбора удаляемых строк реализованы возможности:
        - искать с учётом регистра или не учитывая регистр букв;
        - искать строки, начинающиеся на заданное значение или искать строки, содержащие заданное значение.
        Используются методы:
          - Удалить поэлементно: SELECT и удаление в цикле.
          - Удалить сразу всё: DELETE и одновременное удаление в СУБД.
post("/hotels") - Создание записи с новым отелем.
        Функция: create_hotel_post
put("/hotels/{hotel_id}") - Обновление ВСЕХ данные одновременно для выбранной записи 
        по идентификатору отеля.
        Функция: change_hotel_put
        Реализованы методы:
          - Обновить поэлементно: SELECT и обновление в цикле.
          - Обновить сразу всё: UPDATE и одновременное обновление в СУБД.
patch("/hotels/{hotel_id}") - Обновление каких-либо данных выборочно или всех данных 
        сразу для выбранной записи по идентификатору отеля.
        Функция: change_hotel_patch
"""


router = APIRouter(prefix="/hotels", tags=["Отели"])

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

    ***:return:*** Список отелей или строка с уведомлением, если список отель пуст.

    Если параметр `all_hotels` имеет значение `True`, то остальные
    параметры игнорируются и сразу выводится полный список.

    Список отелей выводится в виде:
    list(info: list(str, str), list(dict(hotel_item: HotelItem) | str)), где:
    - ***info***, это информация, какая страница выводится и сколько элементов на странице;
    - ***list(dict(hotel_item: HotelItem) | str)***, это список выводимых отелей или строка,
    что "Данные отсутствуют".
    """

    # В операторе ниже запрос сохраняется в переменной query. На данный
    # момент запрос еще не выполнен и даже не связан с сеансом.
    # Чтобы выполнить запрос, его можно передать методу execute() объекта session:
    # results = session.execute(query)

    get_hotels_query = select(HotelsORM)
    if not pagination.all_hotels:
        skip = (pagination.page - 1) * pagination.per_page
        get_hotels_query = (get_hotels_query
                            .limit(pagination.per_page)
                            .offset(skip)
                            )
    # Вывод в консоль полученной строки запроса get_hotels_query:
    # print(get_hotels_query.compile(engine, compile_kwargs={"literal_binds": True}))

    async with async_session_maker() as session:
        result = await session.execute(get_hotels_query)
        # Методы для result:
        # - all() чтобы вернуть список с объектом строки для каждой строки результата.
        # - first() чтобы вернуть первую строку результата.
        # - one() чтобы вернуть первую строку результата и вызвать исключение,
        #   если результатов нет или их несколько.
        # - one_or_none() чтобы вернуть первую строку результата или None если
        #   результатов нет, или вызвать исключение если есть более одного результата.
        # Session имеет два дополнительных метода выполнения, которые делают
        # работу со строками (row) с одним значением более удобной в использовании:
        #     scalars() возвращает объект ScalarResult с первым значением каждой
        #               строки результата. Перечисленные выше методы Result
        #               также доступны для этого нового объекта результата.
        #     scalar() возвращает первое значение первой строки результата.

        # result - Это итератор. По нему пройтись можно только один раз.
        # Поэтому присваиваем значения итератора переменной для дальнейшей работы.

        # Примеры работы:

        # hotels_lst = result.all()
        # print(type(hotels_lst), hotels_lst, sep="\n")
        # Вывод (список из кортежей):
        # <class 'list'>
        # [(<src.models.hotels.HotelsORM object at 0x00000207DF53B310>,),
        # (<src.models.hotels.HotelsORM object at 0x00000207DF53B590>,),
        # ..., (<src.models.hotels.HotelsORM object at 0x00000207DF53B9D0>,)]

        hotels_lst = result.scalars().all()
        # print(type(hotels_lst), hotels_lst, sep="\n")
        # Вывод (список):
        # <class 'list'>
        # [<src.models.hotels.HotelsORM object at 0x000002087ABBB8D0>,
        # <src.models.hotels.HotelsORM object at 0x000002087ABBBB50>,
        # ..., <src.models.hotels.HotelsORM object at 0x000002087ABBBF90>]
        # [
        #   {
        #     "title": "Наименование отеля",
        #     "location": "Местонахождение отеля",
        #     "id": 1
        #   },
        #   {
        #     "title": "title Сочи",
        #     "location": "location Сочи",
        #     "id": 2
        #   },
        # ...
        #   {
        #     "title": "Отель Сочи 5 звезд у моря",
        #     "location": "ул. Моря, 1",
        #     "id": 11
        #   }
        # ]

        # hotels_lst = result.scalar()
        # print(type(hotels_lst), hotels_lst, sep="\n")
        # Вывод (один - первый элемент):
        # <class 'src.models.hotels.HotelsORM'>
        # <src.models.hotels.HotelsORM object at 0x000001848337B390>
        # {
        #   "title": "Наименование отеля",
        #   "location": "Местонахождение отеля",
        #   "id": 1
        # }
        # hotels_lst = result.all()
        # print(type(hotels_lst), hotels_lst, sep="\n")
        # Вывод:
        # <class 'list'>
        # [(<src.models.hotels.HotelsORM object at 0x0000013C6EC102D0>,),
        #  (<src.models.hotels.HotelsORM object at 0x0000013C6EC10510>,),
        #  ..., (<src.models.hotels.HotelsORM object at 0x0000013C6EC109D0>,)]

    if pagination.all_hotels:
        status = "Полный список отелей."
    else:
        status = (f"Страница {pagination.page}, установлено отображение {pagination.per_page} "
                  f"элемент(-а/-ов) на странице.")
    status = (status, f"Всего выводится {len(hotels_lst)} элемент(-а/-ов) на странице.")
    if len(hotels_lst) == 0:
        status = (status, f"Данные отсутствуют.")
    else:
        status = (status, hotels_lst)

    # FastAPI самостоятельно конвертирует hotels_lst в приемлемый вид - список,
    # элементы которого словари. В последующем будем делать такое преобразование явно.

    return status


@router.get("/find",
            tags=["Отели"],
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
    print(get_hotels_query.compile(engine, compile_kwargs={"literal_binds": True}), end="\n\n")
    # SELECT hotels.id, hotels.title, hotels.location
    # FROM hotels

    if not (hotel_location or hotel_title):
        return "Не заданы параметры для выбора отеля"

    if hotel_location:
        # get_hotels_query = (get_hotels_query
        #                     .filter_by(location=hotel_location)
        #                     )
        if case_sensitivity:
            get_hotels_query = (get_hotels_query
                                .where(HotelsORM.location.like(location_type+hotel_location+"%"))
                                )
        else:
            get_hotels_query = (get_hotels_query
                                .where(HotelsORM.location.ilike(location_type+hotel_location+"%"))
                                )
    print(get_hotels_query.compile(engine, compile_kwargs={"literal_binds": True}), end="\n\n")
    # case_sensitivity == None
    # starts-with == None
    # SELECT hotels.id, hotels.title, hotels.location
    # FROM hotels
    # WHERE hotels.location ILIKE '%search_text%'

    if hotel_title:
        # get_hotels_query = (get_hotels_query
        #                     .filter_by(title=hotel_title)
        #                     )
        if case_sensitivity:
            get_hotels_query = (get_hotels_query
                                .filter(HotelsORM.title.like(location_type+hotel_title+"%"))
                                )
        else:
            get_hotels_query = (get_hotels_query
                                .filter(HotelsORM.title.ilike(location_type+hotel_title+"%"))
                                )
    print(get_hotels_query.compile(engine, compile_kwargs={"literal_binds": True}), end="\n\n")
    # case_sensitivity == None
    # starts-with == None
    # SELECT hotels.id, hotels.title, hotels.location
    # FROM hotels
    # WHERE hotels.location ILIKE '%search_text%' AND hotels.title ILIKE '%search_text%'

    get_hotels_query = get_hotels_query.order_by(HotelsORM.id)
    print(get_hotels_query.compile(engine, compile_kwargs={"literal_binds": True}), end="\n\n")
    # case_sensitivity == None
    # starts-with == None
    # SELECT hotels.id, hotels.title, hotels.location
    # FROM hotels
    # WHERE hotels.location ILIKE '%search_text%' AND hotels.title ILIKE '%search_text%' ORDER BY hotels.id

    skip = (pagination.page - 1) * pagination.per_page
    get_hotels_query = (get_hotels_query
                        .limit(pagination.per_page)
                        .offset(skip)
                        )
    print(get_hotels_query.compile(engine, compile_kwargs={"literal_binds": True}), end="\n\n")
    # case_sensitivity == None
    # starts-with == None
    # SELECT hotels.id, hotels.title, hotels.location
    # FROM hotels
    # WHERE hotels.location ILIKE '%search_text%' AND hotels.title ILIKE '%search_text%' ORDER BY hotels.id
    #  LIMIT 3 OFFSET 0

    async with async_session_maker() as session:
        result = await session.execute(get_hotels_query)
    hotels_lst = result.scalars().all()

    status = (f"Страница {pagination.page}, установлено отображение {pagination.per_page} "
              f"элемент(-а/-ов) на странице.",
              f"Всего выводится {len(hotels_lst)} элемент(-а/-ов) на странице.")
    if len(hotels_lst) == 0:
        status = (status, f"Данные отсутствуют.")
    else:
        status = (status, hotels_lst)

    # FastAPI самостоятельно конвертирует hotels_lst в приемлемый вид - список,
    # элементы которого словари. В последующем будем делать такое преобразование явно.

    return status


@router.delete("/{hotel_id}",
               tags=["Отели"],
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
        # Получаем объект по первичному ключу
        hotel = await session.get(HotelsORM, hotel_path.hotel_id)
        print(type(hotel), hotel, sep="\n")
        # <class 'src.models.hotels.HotelsORM'>
        # <src.models.hotels.HotelsORM object at 0x000001C6D6DCAA50>

        # если не найден, отправляем статусный код и сообщение об ошибке
        if not hotel:
            return {"status": "Error",
                    "deleted": f"Не найден отель с идентификатором {hotel_path.hotel_id}."}
        await session.delete(hotel)  # Удаляем объект
        await session.commit()  # Подтверждаем удаление
        deleted = {"id": hotel.id,
                   "title": hotel.title,
                   "location": hotel.location, }

    return {"status": "OK", "deleted": deleted}


@router.delete("",
               tags=["Отели"],
               summary="Удаление выбранных записей с выборкой, что "
                       "удалять, по наименованию и адресу отеля",
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
                                 delete_type: Annotated[bool | None,
                                                        Query(alias="delete-type",
                                                              description="Удалить сразу всё (True), или "
                                                                          "удалить поэлементно (False или None)",
                                                              )] = None
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
    - ***:param** delete_type, alias="delete-type":* Удалить сразу всё (True), или Удалить
         поэлементно (False или None).<br>
         Реализованы методы:
         - Удалить поэлементно: SELECT и удаление в цикле.
         - Удалить сразу всё: DELETE и одновременное удаление в СУБД.

    ***:return:*** Словарь: `{"status": str, "deleted method": str, "deleted": str | dict}`, где:

    - ***status***: статус операции (реализованы варианты: OK и Error);
    - ***deleted method***: метод удаления (в случае, если найдены удаляемые отели и
    строка "Ничего не удалялось", если отели для удаления не найдены.
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
    get_hotels_query = select(HotelsORM)
    del_hotels_stmt = delete(HotelsORM)
    # print(get_hotels_query.compile(engine, compile_kwargs={"literal_binds": True}), end="\n\n")
    # SELECT hotels.id, hotels.title, hotels.location
    # FROM hotels
    # print(del_hotels_stmt.compile(engine, compile_kwargs={"literal_binds": True}), end="\n\n")
    # DELETE FROM hotels

    if not (hotel_location or hotel_title):
        return {"status": "Error",
                "deleted method": "Ничего не удалялось",
                "deleted": "Не заданы параметры для выбора отеля"}

    if hotel_location:
        # get_hotels_query = (get_hotels_query
        #                     .filter_by(location=hotel_location)
        #                     )
        if case_sensitivity:
            get_hotels_query = (get_hotels_query
                                .where(HotelsORM.location.like(location_type+hotel_location+"%"))
                                )
            del_hotels_stmt = del_hotels_stmt.where(HotelsORM.location.like(location_type+hotel_location+"%"))
        else:
            get_hotels_query = (get_hotels_query
                                .where(HotelsORM.location.ilike(location_type+hotel_location+"%"))
                                )
            del_hotels_stmt = del_hotels_stmt.where(HotelsORM.location.ilike(location_type+hotel_location+"%"))
    # print(get_hotels_query.compile(engine, compile_kwargs={"literal_binds": True}), end="\n\n")
    # SELECT hotels.id, hotels.title, hotels.location
    # FROM hotels
    # WHERE hotels.location ILIKE '%search_text%'
    # print(del_hotels_stmt.compile(engine, compile_kwargs={"literal_binds": True}), end="\n\n")
    # DELETE FROM hotels WHERE hotels.location ILIKE '%search_text%'

    if hotel_title:
        # get_hotels_query = (get_hotels_query
        #                     .filter_by(title=hotel_title)
        #                     )
        if case_sensitivity:
            get_hotels_query = (get_hotels_query
                                .filter(HotelsORM.title.like(location_type+hotel_title+"%"))
                                )
            del_hotels_stmt = del_hotels_stmt.filter(HotelsORM.title.like(location_type+hotel_title+"%"))
        else:
            get_hotels_query = (get_hotels_query
                                .filter(HotelsORM.title.ilike(location_type+hotel_title+"%"))
                                )
            del_hotels_stmt = del_hotels_stmt.filter(HotelsORM.title.ilike(location_type + hotel_title + "%"))
    # print(get_hotels_query.compile(engine, compile_kwargs={"literal_binds": True}), end="\n\n")
    # print(del_hotels_stmt.compile(engine, compile_kwargs={"literal_binds": True}), end="\n\n")

    get_hotels_query = get_hotels_query.order_by(HotelsORM.id)
    # del_hotels_stmt = del_hotels_stmt.order_by(HotelsORM.id)  # 'Delete' object has no attribute 'order_by'

    # print(get_hotels_query.compile(engine, compile_kwargs={"literal_binds": True}), end="\n\n")
    # case_sensitivity == None, starts-with == None
    # Заданы поиск по hotels.location и по hotels.title
    # SELECT hotels.id, hotels.title, hotels.location
    # FROM hotels
    # WHERE hotels.location ILIKE '%search_text%' AND hotels.title ILIKE '%search_text%' ORDER BY hotels.id

    # print(del_hotels_stmt.compile(engine, compile_kwargs={"literal_binds": True}), end="\n\n")
    # case_sensitivity == None, starts-with == None
    # Заданы поиск по hotels.location и по hotels.title
    # DELETE FROM hotels WHERE hotels.location ILIKE '%search_text%' AND hotels.title ILIKE '%search_text%'

    # Подготовлены переменные:
    # del_hotels_stmt - запрос на удаление на стороне сервера:
    #     DELETE FROM hotels WHERE hotels.location ILIKE '%search_text%' AND hotels.title ILIKE '%search_text%'
    # get_hotels_query - запрос на выборку элементов
    #     SELECT hotels.id, hotels.title, hotels.location
    #     FROM hotels
    #     WHERE hotels.location ILIKE '%search_text%' AND hotels.title ILIKE '%search_text%' ORDER BY hotels.id
    async with async_session_maker() as session:
        result = await session.execute(get_hotels_query)
        hotels_to_delete_lst = result.scalars().all()

        # если не найден, отправляем статусный код и сообщение об ошибке
        if not hotels_to_delete_lst:
            return {"status": "Error",
                    "deleted method": "Ничего не удалялось",
                    "deleted": "Отели с параметром поиска: "
                               f"местонахождение: {hotel_location}, "
                               f"наименование: {hotel_title} "
                               f"не найдены."}

        if delete_type:
            deleted_method = "Массовое удаление - удалить сразу всё (True)"
            # Удалить сразу всё (True)
            # Массовое удаление
            # await session.execute(del_hotels_stmt)
            # В параметре returning указывается, какие столбцы возвращать для удалённых строк.
            # Возвращается список кортежей вида:
            # [(84, 'title ффф', 'location ффф'),
            #  (85, 'title -=-2234 ффф', 'location -=-2234 ффф'),
            #  (86, 'title wed-=-2234 ффф', 'location wed-=-2234 ффф'),
            #  (87, 'title 567-=-2234 ффф', 'location 567-=-2234 ффф')]
            #
            # await session.execute(del_hotels_stmt)
            result = await session.execute(del_hotels_stmt.returning(HotelsORM.id,
                                                                     HotelsORM.title,
                                                                     HotelsORM.location))
            # hotels_to_delete_lst = result.fetchall()
            # print(hotels_to_delete_lst)
            # [(80, 'title ффф', 'location ффф'),
            #  (81, 'title -=-2234 ффф', 'location -=-2234 ффф'),
            #  (82, 'title wed-=-2234 ффф', 'location wed-=-2234 ффф'),
            #  (83, 'title 567-=-2234 ффф', 'location 567-=-2234 ффф')]

            # hotels_to_delete_lst = result.all()
            # print(hotels_to_delete_lst)
            # [(84, 'title ффф', 'location ффф'),
            #  (85, 'title -=-2234 ффф', 'location -=-2234 ффф'),
            #  (86, 'title wed-=-2234 ффф', 'location wed-=-2234 ффф'),
            #  (87, 'title 567-=-2234 ффф', 'location 567-=-2234 ффф')]

            # hotels_to_delete_lst = result.scalars()
            # print(hotels_to_delete_lst)
            # <sqlalchemy.engine.result.ScalarResult object at 0x00000138E4209EF0>

            # hotels_to_delete_lst = result
            # print(hotels_to_delete_lst)
            # <sqlalchemy.engine.result.ChunkedIteratorResult object at 0x000001D93ACD47D0>
            # for hotel in hotels_to_delete_lst:
            #     print(hotel)
            #     # (92, 'title ффф', 'location ффф')
            #     # (93, 'title -=-2234 ффф', 'location -=-2234 ффф')
            #     # (94, 'title wed-=-2234 ффф', 'location wed-=-2234 ффф')
            #     # (95, 'title 567-=-2234 ффф', 'location 567-=-2234 ффф')

        else:
            deleted_method = "Удаляем объекты в цикле - удалить поэлементно (False или None)"
            # Удалить поэлементно (False или None)
            # Удаляем объекты в цикле
            for hotel in hotels_to_delete_lst:
                await session.delete(hotel)
        await session.commit()  # Подтверждаем изменения
        # Переменная hotels_to_delete_lst, полученная при массовом удалении,
        # не пропадает при закрытии сессии: await session.commit()
        # for hotel in hotels_to_delete_lst:
        #     print(hotel)
        #     # (96, 'title ффф', 'location ффф')
        #     # (97, 'title -=-2234 ффф', 'location -=-2234 ффф')
        #     # (98, 'title wed-=-2234 ффф', 'location wed-=-2234 ффф')
        #     # (99, 'title 567-=-2234 ффф', 'location 567-=-2234 ффф')

    # Формируем список удалённых объектов
    deleted = []
    for hotel in hotels_to_delete_lst:
        deleted.append({"id": hotel.id,
                        "title": hotel.title,
                        "location": hotel.location, })
        # print(f"{hotel.id=}\n{hotel.title=}\n{hotel.location=}")
    return {"status": "OK", "deleted method": deleted_method, "deleted": deleted}


@router.post("",
             tags=["Отели"],
             summary="Создание записи с новым отелем",
             )
async def create_hotel_post(hotel_caption: Annotated[HotelCaptionRec,
                                                     Body(openapi_examples={
                                                         "1": {"summary": "Сочи",
                                                               "value": {"title": "title Сочи",
                                                                         "location": "location Сочи"}},
                                                         "2": {"summary": "Дубай",
                                                               "value": {"title": "title Дубай",
                                                                         "location": "location Дубай"}}
                                                     })]):
    """
    ## Функция создаёт запись.

    Параметры (передаются методом Body):
    - ***:param** hotel_title:* title отеля (обязательно)
    - ***:param** hotel_name:* name отеля (обязательно)

    ***:return:*** Статус завершения операции.

    В текущей реализации статус завершения операции всегда один и тот же: OK

    Если работать с БД, то добавятся новые статусы.
    """
    async with async_session_maker() as session:
        # преобразуют модель в словарь Python: HotelCaptionRec.model_dump()
        # Раскрываем (распаковываем) словарь в список именованных аргументов
        # "title"= , "location"=
        add_hotel_stmt = insert(HotelsORM).values(**hotel_caption.model_dump())
        await session.execute(add_hotel_stmt)
        await session.commit()
        status = "OK"

    # global hotels
    #
    # status = "OK"
    # # Если работать с БД, то добавление отеля надо оформить блоком TRY.
    # hotels.append({"id": hotels[-1]["id"] + 1,
    #                "title": hotel_caption.hotel_title,
    #                "name": hotel_caption.hotel_name
    #                })
    return {"status": status}


@router.put("/{hotel_id}",
            tags=["Отели"],
            summary="Обновление ВСЕХ данные одновременно для выбранной записи по идентификатору отеля",
            )
async def change_hotel_put(hotel_path: Annotated[HotelPath, Path()],
                           hotel_caption: Annotated[HotelCaptionRec, Body()],
                           update_type: Annotated[bool | None,
                                                  Query(alias="update-type",
                                                        description="Обновить сразу всё (True) - метод update, или "
                                                                    "обновить поэлементно (False или None)",
                                                        )] = None
                           ):
    """
    ## Функция изменяет (обновляет) ВСЕ данные одновременно

    В ручке PUT мы обязаны передать оба параметра title и name.

    Параметры (передаются в URL):
    - ***:param** hotel_id:* Идентификатор отеля (обязательно).

    Параметры (передаются методом Body):
    - ***:param** title:* Название отеля (обязательно).
    - ***:param** location:* Адрес отеля (обязательно).
    - ***:param** update_type, alias="update-type":* Обновить сразу всё (True) - метод update,
         или обновить поэлементно (False или None).<br>
         Реализованы методы:
         - Обновить поэлементно: SELECT и обновление в цикле.
         - Обновить сразу всё: UPDATE и одновременное обновление в СУБД.

    ***:return:*** Статус завершения операции (текст) и значение статуса операции (число): 0, 1

    Значение статуса завершения операции:
    - 0: все OK.
    - 1: ничего не найдено.
    """
    status = f"Для отеля с идентификатором {hotel_path.hotel_id} ничего не найдено"
    err_type = 1
    async with async_session_maker() as session:
        if update_type:
            # Обновить сразу всё (True) - метод update
            # Обновление через метод update
            update_hotels_stmt = (update(HotelsORM)
                                  .where(HotelsORM.id == hotel_path.hotel_id)
                                  .values(title=hotel_caption.title,
                                          location=hotel_caption.location)
                                  )
            result = await session.execute(update_hotels_stmt)
            updated_rows = result.rowcount
            if updated_rows == 0:
                return {"status": status, "err_type": err_type}
        else:
            # обновить поэлементно (False или None)
            # Получаем объект по первичному ключу
            hotel = await session.get(HotelsORM, hotel_path.hotel_id)

            # если не найден, отправляем статусный код и сообщение об ошибке
            if not hotel:
                return {"status": status, "err_type": err_type}

            # Теоретически, если надо обновлять несколько данных, то тут должен быть цикл.
            hotel.title = hotel_caption.title
            hotel.location = hotel_caption.location
        await session.commit()  # Подтверждаем изменение
    status = "OK"
    err_type = 0
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
async def change_hotel_patch(hotel_path: Annotated[HotelPath,
                                                   Path(examples=[{
                                                                   "hotel_id": 1
                                                                   }
                                                                  ]
                                                        )
                                                   ],
                             hotel_caption: Annotated[HotelCaptionOpt,
                                                      Body(examples=[{
                                                                      "title": "title отеля",
                                                                      "location": "name отеля",
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

    err_type = 1
    status = f"Для отеля с идентификатором {hotel_path.hotel_id} ничего не найдено"

    if not (hotel_caption.title or hotel_caption.location):
        status = "Не заданы параметры для выбора отеля"
        return {"status": status, "err_type": err_type}

    async with async_session_maker() as session:
        # Получаем объект по первичному ключу
        hotel = await session.get(HotelsORM, hotel_path.hotel_id)

        # если не найден, отправляем статусный код и сообщение об ошибке
        if not hotel:
            return {"status": status, "err_type": err_type}

        if hotel_caption.title:
            hotel.title = hotel_caption.title
        if hotel_caption.location:
            hotel.location = hotel_caption.location
        await session.commit()  # Подтверждаем изменение
    err_type = 0
    status = "OK"
    return {"status": status, "err_type": err_type}
