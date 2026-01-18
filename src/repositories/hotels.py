from typing import Union

from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.exc import MultipleResultsFound

from src.api.dependencies.dependencies import pagination_pages
from src.repositories.base import BaseRepository, BaseRepositoryMyCode
from src.models.hotels import HotelsORM
from src.schemas.hotels import HotelPydanticSchema


# HotelsRepositoryLesson - код репозитария из урока.
# В уроке назывался class HotelsRepository:
class HotelsRepositoryLesson:
    model = HotelsORM

    async def get_all(
            self,
            location,
            title,
            limit,
            offset,
    ):
        query = select(HotelsORM)
        if location:
            query = query.filter(func.lower(HotelsORM.location).contains(location.strip().lower()))
        if title:
            query = query.filter(func.lower(HotelsORM.title).contains(title.strip().lower()))
        query = (
            query
            .limit(limit)
            .offset(offset)
        )
        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)

        return result.scalars().all()


# HotelsRepositoryMyCode - мой код репозитария.
# В уроке назывался class HotelsRepository:
class HotelsRepositoryMyCode(BaseRepositoryMyCode):
    model = HotelsORM
    schema = HotelPydanticSchema

    # # См. пояснение перед созданием класса BaseRepositoryMyCode
    # def __init__(self, session):
    #     super().__init__(session, HotelsORM)

    async def get_all(self):
        """
        Метод класса. Выбирает все строки. Использует родительский метод get_rows.
        Возвращает пустой список: [] или список из выбранных строк:
        [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
         HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
         ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
        Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        """
        result = await super().get_rows(show_all=True)
        # Возвращает пустой список: [] или список:
        # [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
        #  HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
        #  ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        status = ("Полный список отелей.",
                  f"Всего выводится {len(result)} элемент(-а/-ов) на странице.")
        # if len(result) == 0:
        #     function_output = (status, f"Данные отсутствуют.")
        # else:
        #     function_output = (status, result)
        return status, ("Данные отсутствуют." if len(result) == 0 else result)

    async def get_limit(self,
                        query=None,
                        title=None,
                        location=None,
                        # per_page=pagination_pages["per_page"],
                        # page=pagination_pages["page"],
                        per_page=None,
                        page=None,
                        ):
        """
        Метод класса. Выбирает заданное количество строк с
        заданным смещением. Использует родительский метод get_rows.

        :param query: SQL-Запрос. Если простой SELECT-запрос на выборку,
            то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :param title: Наименование отеля
        :param location: Адрес отеля
        :param per_page: Количество элементов на странице (должно быть >=1 и
            <=30, по умолчанию значение 3).
        :param page: Номер страницы для вывода (должно быть >=1, по умолчанию
            значение 1).
        :return: Возвращает пустой список: [] или список:
            [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
             HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
             ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
            Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        """

        if query is None:
            query = select(self.model)

        if title:
            query = query.filter(func.lower(self.model.title)
                                 .contains(title.strip().lower()))
        if location:
            query = query.filter(func.lower(self.model.location)
                                 .contains(location.strip().lower()))
        result = await super().get_rows(query=query,
                                        per_page=per_page,
                                        page=page
                                        )
        # Возвращает пустой список: [] или список:
        # [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
        #  HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
        #  ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        status = (f'Страница {page}, установлено отображение '
                  f'{per_page} элемент(-а/-ов) на странице.',
                  f"Всего выводится {len(result)} элемент(-а/-ов) на странице.")
        # if len(result) == 0:
        #     function_output = (status, f"Данные отсутствуют.")
        # else:
        #     function_output = (status, result)
        return status, ("Данные отсутствуют." if len(result) == 0 else result)

    async def get_one_or_none_my_err(self,
                                     query=None,
                                     title=None,
                                     location=None,
                                     **filtering,
                                     ):
        """
        Метод класса. Возвращает одну строку или None. Если получено более
        одной строки, то поднимается исключение MultipleResultsFound.
        Использует родительский метод get_rows.

        :param query: SQL-Запрос. Если простой SELECT-запрос на выборку,
            то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :param title: Наименование отеля.
        :param location: Адрес отеля.
        :param filtering: Значения фильтра для выборки объекта. Используется
            фильтр только на точное равенство: filter_by(**filtering), который
            преобразуется в конструкцию (для примера): WHERE hotels.id = 188

        :return: Возвращает первую строку результата или None если результатов нет,
            или вызывает исключение если есть более одного результата.
            - список, содержащий один элемент, преобразованный к схеме Pydantic (self.schema):
              [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16)]
            - ошибку MultipleResultsFound, если более одного результата.
            - None если результатов нет.
        Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        """
        if query is None:
            query = select(self.model)

        if title:
            query = query.filter(func.lower(HotelsORM.title)
                                 .contains(title.strip().lower()))
        if location:
            query = query.filter(func.lower(HotelsORM.location)
                                 .contains(location.strip().lower()))

        query = query.filter_by(**filtering)

        result = await super().get_rows(query=query, limit=2, offset=0)
        # Возвращает пустой список: [] или список:
        # [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16]
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        # В случае, если возвращается два экземпляра:
        # [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16,
        #  HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17)]
        # то требуется поднять ошибку sqlalchemy.orm.exc.MultipleResultsFound.
        # Так написано в документации:
        # - method sqlalchemy.engine.Result.one_or_none() → Row[_TP] | None¶
        # https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Result.one_or_none
        # -  method sqlalchemy.orm.Query.one_or_none() → _T | None¶
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.one_or_none

        if len(result) > 1:
            raise MultipleResultsFound
        return result if result else None
        # return result.scalars().one_or_none()

    # async def add(self, added_data: BaseModel, **kwargs):
    #     """
    #     Метод класса. Добавляет один объект в базу, используя метод
    #     insert. Служит обёрткой для родительского метода add.
    #
    #     Возвращает добавленный объект.
    #     """
    #     # Теоретически, эта функция не нужна, так как наследуется
    #     # от родителя из класса BaseRepositoryMyCode. Но вставлена
    #     # на случай, если потребуется дополнительная обработка.
    #
    #     result = await super().add(added_data, **kwargs)
    #     return result

    async def edit(self,
                   edited_data: BaseModel,
                   edit_stmt=None,
                   exclude_unset: bool = False,
                   **filtering):  # -> None:
        """
        Метод класса. Редактирует один объект в базе, используя метод
        update. Служит обёрткой для родительского метода edit.

        :param edited_data: Новые значения для внесения в выбранную запись.
        :param edit_stmt: SQL-Запрос на редактирование. Если простой UPDATE-запрос на
            редактирование, то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :param exclude_unset: Редактировать все поля модели (True) или
               редактировать только те поля, которым явно присвоено значением
               (даже если присвоили None).
        :param filtering: Значения фильтра для выборки объекта. Используется
            фильтр только на точное равенство: filter_by(**filtering), который
            преобразуется в конструкцию (для примера): WHERE hotels.id = 188

        :return: Возвращает словарь:
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
        result = await super().edit(edited_data, edit_stmt, exclude_unset, **filtering)
        if len(result) == 0:
            status = f"Для отеля с идентификатором {filtering['id']} ничего не найдено"
            err_type = 1
            return {"status": status, "err_type": err_type, "updated rows": None}
        status = "OK"
        err_type = 0
        return {"status": status, "err_type": err_type, "updated rows": result}

    async def delete(self, delete_stmt=None, **filtering):  # -> None:
        """
        Метод класса. Удаляет объект или объекты в базе, используя метод
        delete. Служит обёрткой для родительского метода delete.

        :param delete_stmt: SQL-Запрос. Если простой SELECT-запрос на выборку,
            то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :param filtering: Значения фильтра для выборки объекта. Используется
            фильтр только на точное равенство: filter_by(**filtering), который
            преобразуется в конструкцию (для примера): WHERE hotels.id = 188
        :return: Возвращает словарь:
            {"status": str, "err_type": int, "deleted rows": list(dict | [])},
            где:
            - status: . Текстовое описание результата операции.
            - err_type: . Код результата операции.
              Принимает значения:
              - 0 (OK - выполнено нормально, без ошибок).
              - 1 (Для объекта с указанным идентификатором ничего не найдено).
            - deleted_rows: Список, содержащий удалённый объект. Выводится
              в виде списка, содержащего элементы объекта HotelsORM. Если
              не найдены объекты для удаления, выводится None (null).
        """
        result = await super().delete(delete_stmt, **filtering)
        if len(result) == 0:
            status = f"Не найден(ы) отель (отели) для удаления"
            err_type = 1
            return {"status": status, "err_type": err_type, "deleted rows": None}
        status = "OK"
        err_type = 0
        return {"status": status, "err_type": err_type, "deleted rows": result}

    async def get_id(self, hotel_id: Union[int | None] = None):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (поле self.model.id) один
        объект в базе, используя метод get. Служит обёрткой для родительского
        метода get_id.

        :param hotel_id: Идентификатор выбираемого объекта.

        :return: Возвращает словарь:
        {"status": str, "err_type": int, "got row": dict},
        где:
        - status: str. Текстовое описание результата операции.
        - err_type: int. Код результата операции.
          Принимает значения:
          - 0 (OK - выполнено нормально, без ошибок).
          - 1 (Для объекта с указанным идентификатором ничего не найдено).
          - 2 (Не указан идентификатор отеля для выборки).
        - got_row: Выбранный объект. Выводятся в виде словаря элементы
            объекта HotelsORM.

        """
        if hotel_id is None:
            status = f"Не указан идентификатор отеля для выборки"
            err_type = 2
            return {"status": status, "err_type": err_type, "got row": None}

        # result = await self.session.get(self.model, object_id)
        result = await super().get_id(hotel_id)
        # result: None или <src.models.hotels.HotelsORM object at 0x0000023FB96EAD90>
        # Возвращает пустой список: [] или объект:
        # HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16)
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        if not result:
            status = f"Для отеля с идентификатором {hotel_id} ничего не найдено"
            err_type = 1
            return {"status": status, "err_type": err_type, "got row": None}
        status = "OK"
        err_type = 0
        return {"status": status, "err_type": err_type, "got row": result}


# HotelsRepository = HotelsRepositoryLesson
HotelsRepository = HotelsRepositoryMyCode
