from typing import Union

from sqlalchemy import select, insert, update, delete
from sqlalchemy import select as sa_select  # Для реализации SQL команды SELECT
from sqlalchemy import insert as sa_insert  # Для реализации SQL команды INSERT
from sqlalchemy import update as sa_update  # Для реализации SQL команды UPDATE
from sqlalchemy import delete as sa_delete  # Для реализации SQL команды DELETE

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.dependencies_consts import pagination_pages


from src.database import engine

# engine нужен, чтобы использовать диалект SQL:
# add_stmt = (sa_insert(self.model)
#             # .returning(self.model)
#             .values(**added_data.model_dump()
#                     )
#             )
# print(add_stmt.compile(compile_kwargs={"literal_binds": True}))
# # Вывод: INSERT INTO hotels (title, location)
# #        VALUES ('title_string', 'location_string')
# print(add_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
# # Вывод: INSERT INTO hotels (title, location)
# #        VALUES ('title_string', 'location_string')
# #        RETURNING hotels.id


# Использование конструкции в родительском классе для изменения атрибута класса:
#         BaseRepositoryMyCode.model = model  # Атрибут класса
# когда, например, в методе __init__ родительского класса меняется атрибут класса
# и использование конструкции в дочернем классе для инициализации класса:
#         super().__init__(session, HotelsORM)
# приводит к следующему:
# У всех созданных объектов родительского класса BaseRepositoryMyCode и созданных
# объектов дочернего класса HotelsRepositoryMyCode будет меняться атрибут класса
# BaseRepositoryMyCode.model и HotelsRepositoryMyCode.model - см. пример в
# файле tests/test_model_cls.py (этот файл на гитхаб не выкладывается).
# Код может быть такой (для примера):
#
# class BaseRepositoryMyCode:
#     model = None
#
#     def __init__(self, session, model):
#         self.session = session
#         # self.model = model  # Атрибут экземпляра класса
#         BaseRepositoryMyCode.model = model  # Атрибут класса
#     ...
#
# class HotelsRepositoryMyCode(BaseRepositoryMyCode):
#
#     def __init__(self, session):
#         super().__init__(session, HotelsORM)
#     ...
#
# Если же в дочернем классе происходит явное переопределение атрибута класса, то
# изменение атрибута в родительском классе не влечёт за собой изменение атрибутов
# класса в созданных объектах дочернего класса. Код ниже меняет у всех созданных
# объектов родительского класса BaseRepositoryMyCode атрибут model, но не меняет
# аналогичный атрибут model у всех созданных объектов дочернего класса
# HotelsRepositoryMyCode.
# Код может быть такой (для примера):
#
# class BaseRepositoryMyCode:
#     model = None
#
#     def __init__(self, session, model):
#         self.session = session
#         # self.model = model  # Атрибут экземпляра класса
#         BaseRepositoryMyCode.model = model  # Атрибут класса
#     ...
#
# class HotelsRepositoryMyCode(BaseRepositoryMyCode):
#     model = HotelsORM
#
#     def __init__(self, session):
#         super().__init__(session, HotelsORM)
#     ...
#
# Чтобы не влиять на атрибут model родительского класса и, тем самым, не влиять на
# атрибут model у всех созданных объектов родительского класса BaseRepositoryMyCode,
# требуется не изменять этот атрибут при работе с родительским классом и с дочерними
# классами. Для этого можно использовать код, когда дочерний класс не имеет своего
# метода __init__, а пользуется наследуемым от родителя методом __init__. Но при
# этом в дочернем классе происходит явное переопределение атрибута model.
# Код может быть такой (для примера):
#
# class BaseRepositoryMyCode:
#     model = None
#
#     def __init__(self, session):
#         self.session = session
#     ...
# class HotelsRepositoryMyCode(BaseRepositoryMyCode):
#     model = HotelsORM
#     ...

class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session: AsyncSession):
        self.session = session

    # Сделаны методы:
    #
    # - get_filtered. Выбирает строки по указанным фильтрам из таблицы.
    #       Использует фильтры: Использует фильтры: .filter(*filter), .filter_by(**filter_by).
    #       Возвращает пустой список: [] или список из выбранных строк, тип
    #       возвращаемых элементов преобразован к схеме Pydantic: self.schema.
    # - get_rows. Выбирает заданное количество строк с заданным смещением.
    #       Возвращает пустой список: [] или список из выбранных строк, тип
    #       возвращаемых элементов преобразован к схеме Pydantic: self.schema.
    # - add. Добавляет один объект в базу, используя метод insert.
    #       Возвращает список, содержащий добавленный объект.
    # - edit. Редактирует один объект в базе, используя метод update.
    #       Возвращает пустой список: [] или список из выбранных строк, тип
    #       возвращаемых элементов преобразован к схеме Pydantic: self.schema.
    #       Возвращаемый список содержит отредактированные элементы.
    # - edit_id. Выбирает по идентификатору (поле self.model.id) один объект в базе,
    #       используя метод get.
    #       Редактирует один объект в базе, обновление реализовано через обновление
    #       атрибутов объекта: setattr(updated_object, key, value).
    #       Возвращает None или отредактированный объект, преобразованный к
    #       схеме Pydantic: self.schema.
    # - delete. Удаляет один объект в базе, используя метод delete.
    #       Возвращает пустой список: [] или список из выбранных строк, тип
    #       возвращаемых элементов преобразован к схеме Pydantic: self.schema.
    #       Возвращаемый список содержит удалённые элементы.
    # - delete_id. Выбирает по идентификатору (по первичному ключу) - поле
    #       self.model.id один объект в базе, используя метод get, удаляет
    #       методом session.delete.
    #       Используются методы:
    #       - session.get(RoomsORM, object_id) для получения объекта по ключу
    #       - session.delete(room_object) для удаления объекта room_object.
    #       Возвращает None или удалённый объект, преобразованный к схеме
    #       Pydantic: self.schema.
    # - get_id. Выбирает по идентификатору (поле self.model.id) один
    #       объект в базе, используя метод get.
    #       Возвращает None или объект, преобразованный к схеме
    #       Pydantic: self.schema.
    # - get_one_or_none. Выбирает объекты из базы по запросу с фильтрами
    #       filter_by(**filtering). Использует штатный метод one_or_none().
    #       Возвращает первую строку результата или None если результатов нет.
    #       Вызывает исключение если есть более одного результата.

    async def get_filtered(self, *filter, **filter_by):
        """
        Метод класса. Выбирает строки по указанным фильтрам из таблицы.
        Использует фильтры: .filter(*filter), .filter_by(**filter_by).

        Реализован в соответствии с кодом из урока - чтобы понять, как работает
        выборка отелей со свободными номерами или выборка свободных номеров.

        :return: Возвращает пустой список: [] или список из выбранных строк:
                [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
                 HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
                 ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
                Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        """
        # query = (
        #     select(self.model)
        #     .filter(*filter)
        #     .filter_by(**filter_by)
        # )
        # result = await self.session.execute(query)
        # return [self.schema.model_validate(model) for model in result.scalars().all()]
        return await self.get_rows(*filter, show_all=True, **filter_by)

    async def get_rows(self, *filter,
                       query=None,
                       per_page=pagination_pages["per_page"],
                       page=pagination_pages["page"],
                       # offset=(pagination_pages["page"] - 1) * pagination_pages["per_page"],
                       # limit=pagination_pages["per_page"],
                       #         :param offset: Количество строк, пропускаемых при выборке.
                       #                 Имеет значение по умолчанию.
                       #                 Не используется, если параметр show_all=True.
                       #         :param limit: Количество строк, выбираемых из базы данных.
                       #                 Имеет значение по умолчанию.
                       #                 Не используется, если параметр show_all=True.
                       show_all=None,
                       order_by=True,
                       **filter_by):
        """
        Метод класса. Выбирает заданное количество строк с заданным смещением.

        :param filter: Фильтры для запроса - конструкция .filter(*filter).
        :param query: SQL-Запрос. Если простой SELECT-запрос на выборку,
                то он формируется внутри метода. В качестве значений могут
                приходить запросы, связанные с разными фильтрами.
        :param per_page: Количество элементов на странице (должно быть >=1 и <=30,
            по умолчанию значение 3).
            Не используется, если параметр show_all=True.
        :param page: Номер страницы для вывода (должно быть >=1, по умолчанию
            значение 1).
            Не используется, если параметр show_all=True.
        :param show_all: Выбирать сразу (True) все записи, соответствующие
                запросу, или выполнить ограниченную выборку (False или None).
                Может отсутствовать.
        :param order_by: Упорядочивать перед выборкой по полю self.model.id
                записи, соответствующие запросу (True), или выбирать,
                основываясь на порядке в базе данных (False или None).
                Может отсутствовать.
        :param filter_by: Фильтры для запроса - конструкция .filter_by(**filter_by).

        :return: Возвращает пустой список: [] или список из выбранных строк:
                [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
                 HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
                 ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
                Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        """

        if query is None:
            query = sa_select(self.model)

            query = (query
                     .filter(*filter)
                     .filter_by(**filter_by)
                     )

        if not show_all:
            limit = per_page
            offset = ((page - 1) * per_page)
            query = query.limit(limit).offset(offset)

        if order_by:
            query = query.order_by(self.model.id)

        result = await self.session.execute(query)
        # HotelPydanticSchema.model_validate() получает на входе словарь, ключи которого
        # будут считаться именами полей в схеме, или сущностью HotelPydanticSchema
        # hotel - это сущность HotelsORM (модель).
        # from_attributes – Whether to extract data from object attributes.
        # То есть, доставать атрибуты из других экземпляров классов.
        # from src.schemas.hotels import HotelPydanticSchema
        # result_pydantic_schema = [HotelPydanticSchema.model_validate(hotel,
        #                                                              from_attributes=True)
        #                           for hotel in result.scalars().all()]
        # И надо в таком случае везде писать from_attributes=True.

        # Чтобы это убрать, добавляем в Pydantic-схему HotelPydanticSchema параметр
        # model_config = ConfigDict(from_attributes=True)

        # Так как в Pydantic-схеме HotelPydanticSchema добавили параметр
        # model_config = ConfigDict(from_attributes=True)
        # то по умолчанию будет использоваться значение from_attributes=True

        result_pydantic_schema = [self.schema.model_validate(row_model)
                                  for row_model in result.scalars().all()]
        # return result.scalars().all()
        return result_pydantic_schema

    async def add(self, added_data: BaseModel, **kwargs):
        """
        Метод класса. Добавляет один объект в базу, используя метод insert.

        :param added_data: Добавляемые данные.
        :param kwargs: Возможные иные именованные аргументы (не используются).
        :return: Возвращает список, содержащий добавленный объект.
        """
        # add_stmt = (sa_insert(self.model)
        #             # .returning(self.model)
        #             .values(**added_data.model_dump()
        #                     )
        #             )
        # print(add_stmt.compile(compile_kwargs={"literal_binds": True}))
        # # Вывод: INSERT INTO hotels (title, location)
        # #        VALUES ('title_string', 'location_string')
        # print(add_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
        # # Вывод: INSERT INTO hotels (title, location)
        # #        VALUES ('title_string', 'location_string')
        # #        RETURNING hotels.id
        add_stmt = (sa_insert(self.model)
                    .returning(self.model)
                    .values(**added_data.model_dump()
                            )
                    )
        # print(add_stmt.compile(compile_kwargs={"literal_binds": True}))
        # Вывод: INSERT INTO hotels (title, location)
        #        VALUES ('title_string', 'location_string')
        #        RETURNING hotels.id, hotels.title, hotels.location
        # print(add_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
        # Вывод: INSERT INTO hotels (title, location)
        #        VALUES ('title_string', 'location_string')
        #        RETURNING hotels.id, hotels.title, hotels.location

        result = await self.session.execute(add_stmt)
        # result_pydantic_schema = [self.schema.model_validate(row_model,
        #                                                      from_attributes=True)
        #                           for row_model in result.scalars().all()]
        # result_pydantic_schema = [self.schema.model_validate(row_model)
        #                           for row_model in result.scalars().all()]
        # return result.scalars().all()
        # return result_pydantic_schema
        model = result.scalars().one()
        result_pydantic_schema = self.schema.model_validate(model)
        return result_pydantic_schema

    async def add_bulk(self, added_data: list[BaseModel], **kwargs):
        """
        Метод класса. Добавляет один объект в базу, используя метод insert.

        :param added_data: Добавляемые данные.
        :param kwargs: Возможные иные именованные аргументы (не используются).
        :return: Возвращает список, содержащий добавленный объект.
        """
        if added_data == []:
            return

        add_stmt = (sa_insert(self.model)
                    # .returning(self.model)
                    .values([item.model_dump() for item in added_data]
                            )
                    )
        # print(add_stmt.compile(compile_kwargs={"literal_binds": True}))
        # Вывод: INSERT INTO rooms_facilities (room_id, facility_id)
        #        VALUES (:room_id_m0, :facility_id_m0),
        #               (:room_id_m1, :facility_id_m1)
        #
        #        INSERT INTO rooms_facilities (room_id, facility_id)
        #        VALUES (51, 1), (51, 2)
        # add_stmt = (sa_insert(self.model)
        #             .returning(self.model)
        #             .values([item.model_dump() for item in added_data]
        #                     )
        #             )
        # print(add_stmt.compile(compile_kwargs={"literal_binds": True}))
        # Вывод: INSERT INTO rooms_facilities (room_id, facility_id)
        #        VALUES (:room_id_m0, :facility_id_m0),
        #               (:room_id_m1, :facility_id_m1)
        #        RETURNING rooms_facilities.id,
        #                  rooms_facilities.room_id,
        #                  rooms_facilities.facility_id
        #
        #        INSERT INTO rooms_facilities (room_id, facility_id)
        #        VALUES (52, 1), (52, 2)
        #        RETURNING rooms_facilities.id,
        #                  rooms_facilities.room_id,
        #                  rooms_facilities.facility_id

        # result = await self.session.execute(add_stmt)
        # result: <sqlalchemy.engine.result.ChunkedIteratorResult object at 0x0000015D085105D0>
        await self.session.execute(add_stmt)
        # result_pydantic_schema = [self.schema.model_validate(row_model,
        #                                                      from_attributes=True)
        #                           for row_model in result.scalars().all()]
        # result_pydantic_schema = [self.schema.model_validate(row_model)
        #                           for row_model in result.scalars().all()]
        # return result.scalars().all()
        # return result_pydantic_schema

    async def edit(self,
                   edited_data: BaseModel,
                   edit_stmt=None,
                   exclude_unset: bool = False,
                   **filtering):  # -> None:
        """
        Метод класса. Редактирует один объект в базе, используя метод update.

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

        :return: Возвращает пустой список: [] или список:
               [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
                HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
                ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
               Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema.
               Возвращаемый список содержит отредактированные элементы.
        """
        # edit_stmt = (sa_update(self.model)
        #              .filter_by(**filtering)
        #              .values(**edited_data.model_dump(exclude_unset=exclude_unset))
        #              .returning(self.model)
        #              )
        if edit_stmt is None:
            edit_stmt = sa_update(self.model)
        edit_stmt = (edit_stmt
                     .filter_by(**filtering)
                     .values(**edited_data.model_dump(exclude_unset=exclude_unset))
                     .returning(self.model)
                     )
        # print(edit_stmt.compile(compile_kwargs={"literal_binds": True}))
        # Вывод: UPDATE hotels SET title='New_string', location='New_string'
        #        WHERE hotels.id = 213 RETURNING hotels.id, hotels.title, hotels.location
        result = await self.session.execute(edit_stmt)
        # result = <sqlalchemy.engine.result.ChunkedIteratorResult object at 0x000002330C349350>
        # result_pydantic_schema = [self.schema.model_validate(row_model,
        #                                                      from_attributes=True)
        #                           for row_model in result.scalars().all()]
        result_pydantic_schema = [self.schema.model_validate(row_model)
                                  for row_model in result.scalars().all()]
        # Получаем пустой список: [] или список:
        # [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
        #  HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
        #  ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        # return result
        return result_pydantic_schema

    async def edit_id(self,
                      edited_data: BaseModel,
                      object_id=None,
                      exclude_unset: bool = False):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (поле self.model.id) один
        объект в базе, используя метод get.
        Редактирует один объект в базе, обновление реализовано через обновление
        атрибутов объекта: setattr(updated_object, key, value).

        :param edited_data: Новые значения для внесения в выбранную запись.
        :param object_id: Идентификатор выбираемого объекта.
        :param exclude_unset: Редактировать все поля модели (True) или
            редактировать только те поля, которым явно присвоено значением
            (даже если присвоили None).

        :return: Возвращает None или отредактированный объект, преобразованный
            к схеме Pydantic: self.schema.
        """
        # Получаем объект по первичному ключу
        result = await self.session.get(self.model, object_id)
        # result: None или <src.models.hotels.HotelsORM object at 0x0000023FB96EAD90>
        if result:
            # Например, если задано значение только для поля location, то тогда
            # - словарь: edited_data.model_dump(exclude_unset=True)
            #   будет иметь значения:
            #   {'location': 'new_location_string'}
            # - словарь: edited_data.model_dump(exclude_unset=False)
            #   будет иметь значения:
            #   {'title': None, 'location': 'new_location_string'}
            # Устанавливаем значения, для тех атрибутов, которые задал пользователь
            # см. How to update sqlalchemy orm object by a python dict
            # https://www.iditect.com/program-example/how-to-update-sqlalchemy-orm-object-by-a-python-dict.html
            valid_keys = set(self.model.__table__.columns.keys())
            # self.model.__table__.columns.keys(): ['id', 'title', 'location']
            # set(self.model.__table__.columns.keys()): {'location', 'id', 'title'}

            for key, value in edited_data.model_dump(exclude_unset=exclude_unset).items():
                if key in valid_keys:
                    # Updates only the attributes of the SQLAlchemy
                    # ORM object that correspond to valid table columns
                    setattr(result, key, value)

            # Преобразование объекта SQLAlchemy в Pydantic
            # result_pydantic_schema = self.schema.model_validate(result, from_attributes=True)
            result_pydantic_schema = self.schema.model_validate(result)
            # Получаем элемент HotelPydanticSchema(title='title_string',
            #                                      location='location_string',
            #                                      id=16).
            # Тип возвращаемого элемента преобразован к схеме Pydantic: self.schema
            return result_pydantic_schema
        return None

    async def delete(self, delete_stmt=None, **filtering):  # -> None:
        """
        Метод класса. Удаляет один объект в базе, используя метод delete.

        :param delete_stmt: SQL-Запрос на удаление. Если простой DELETE-запрос на
            удаление, то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :param filtering: Значения фильтра для выборки объекта. Используется
            фильтр только на точное равенство: filter_by(**filtering), который
            преобразуется в конструкцию (для примера): WHERE hotels.id = 188
        :return: Возвращает
            - пустой список: []
             или
            - список:
              [HotelPydanticSchema(title='title_string_1',
                                   location='location_string_1', id=16),
               HotelPydanticSchema(title='title_string_2',
                                   location='location_string_2', id=17),
               ..., HotelPydanticSchema(title='title_string_N',
                                        location='location_string_N', id=198)]
              Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
              Возвращаемый список содержит удалённые элементы.
        """
        # delete_stmt = sa_delete(self.model).filter_by(**filtering).returning(self.model)
        if delete_stmt is None:
            delete_stmt = sa_delete(self.model)
        # print(delete_stmt.compile(compile_kwargs={"literal_binds": True}))
        delete_stmt = delete_stmt.filter_by(**filtering).returning(self.model)
        # print(delete_stmt.compile(compile_kwargs={"literal_binds": True}))
        # DELETE FROM hotels WHERE hotels.id = 188
        # RETURNING hotels.id, hotels.title, hotels.location

        result = await self.session.execute(delete_stmt)
        # result = <sqlalchemy.engine.result.ChunkedIteratorResult object at 0x000002330C349350>
        # result_pydantic_schema = [self.schema.model_validate(row_model,
        #                                                      from_attributes=True)
        #                           for row_model in result.scalars().all()]
        result_pydantic_schema = [self.schema.model_validate(row_model)
                                  for row_model in result.scalars().all()]
        # Получаем пустой список: [] или список:
        # [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
        #  HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
        #  ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        # return result
        return result_pydantic_schema

    async def delete_id(self, object_id: int):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (по первичному ключу) -
        поле self.model.id один объект в базе, используя метод get, удаляет
        методом session.delete.
        Используются методы:
        - session.get(RoomsORM, object_id) для получения объекта по ключу
        - session.delete(room_object) для удаления объекта room_object.

        :param object_id: Идентификатор выбираемого объекта.
        :return: Возвращает None или удалённый объект, преобразованный
            к схеме Pydantic: self.schema.
        """
        result = await self.session.get(self.model, object_id)
        # result: None или <src.models.hotels.HotelsORM object at 0x0000023FB96EAD90>
        # return result
        # Шаг 4: Преобразование объекта SQLAlchemy в Pydantic
        if result:

            # result_pydantic_schema = self.schema.model_validate(result, from_attributes=True)
            result_pydantic_schema = self.schema.model_validate(result)
            # Получаем элемент HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16).
            # Тип возвращаемого элемента преобразован к схеме Pydantic: self.schema

            # Deleting
            # The Session.delete() method places an instance into the
            # Session’s list of objects to be marked as deleted:
            # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#deleting
            await self.session.delete(result)
            # print(type(self.session.deleted))
            #       <class 'sqlalchemy.cyextension.collections.IdentitySet'>
            # print(self.session.deleted)
            #       IdentitySet([<src.models.rooms.RoomsORM object at 0x000002E1471F6F90>])
            # По поводу IdentitySet:
            # в venv\Lib\site-packages\sqlalchemy\util\_collections.py импортируется.
            # описывается как:
            # A set that considers only object id() for uniqueness.
            # This strategy has edge cases for builtin types- it's possible to have
            # two 'foo' strings in one of these sets, for example.  Use sparingly.
            # Набор, который учитывает только идентификатор объекта() для определения уникальности.
            # У этой стратегии есть крайние варианты для встроенных типов - например, можно использовать
            # две строки 'foo' в одном из этих наборов.  Используйте с осторожностью.
            #
            # Раздел в справке "Data Manipulation with the ORM"
            # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html
            # Также:
            # https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.delete
            #  method sqlalchemy.orm.Session.delete(instance: object) → None
            # Mark an instance as deleted.
            # The object is assumed to be either persistent or detached when passed; after
            # the method is called, the object will remain in the persistent state until the
            # next flush proceeds. During this time, the object will also be a member of the
            # Session.deleted collection.
            # Получаем все элементы множества self.session.deleted: IdentitySet
            # result_pydantic_schema_deleted = [self.schema.model_validate(row_model)
            #                                   for row_model in self.session.deleted]
            return result_pydantic_schema
        return None

    async def get_id(self, object_id: int):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (поле self.model.id) один
        объект в базе, используя метод get.

        :param object_id: Идентификатор выбираемого объекта.
        :param pydantic_schema: Схема Pydantic, к которой надо преобразовывать
            итоговый результат. Если не задано (PydanticSchema=None), то
            принимает значение по умолчанию: self.schema

        :return: Возвращает None или объект, преобразованный к схеме Pydantic: self.schema.
        """

        result = await self.session.get(self.model, object_id)
        # result: None или <src.models.hotels.HotelsORM object at 0x0000023FB96EAD90>
        # return result
        # Шаг 4: Преобразование объекта SQLAlchemy в Pydantic
        if result:
            # result_pydantic_schema = self.schema.model_validate(result, from_attributes=True)

            result_pydantic_schema = self.schema.model_validate(result)
            # Получаем элемент HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16).
            # Тип возвращаемого элемента преобразован к схеме Pydantic: self.schema
            return result_pydantic_schema
        return None

    async def get_one_or_none(self,
                              query=None,
                              pydantic_schema=None,
                              **filtering):  # -> None:
        """
        Метод класса. Выбирает объекты из базы по запросу с
        фильтрами filter_by(**filtering).
        Использует штатный метод one_or_none().

        :param query: SQL-Запрос. Если простой SELECT-запрос на выборку,
            то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :param pydantic_schema: Схема Pydantic, к которой надо преобразовывать
            итоговый результат. Если не задано (PydanticSchema=None), то
            принимает значение по умолчанию: self.schema
        :param filtering: Значения фильтра для выборки объекта. Используется
            фильтр только на точное равенство: filter_by(**filtering), который
            преобразуется в конструкцию (для примера): WHERE hotels.id = 188

        :return: Возвращает первую строку результата или None если результатов нет,
            или вызывает исключение если есть более одного результата.
            - список, содержащий один элемент, преобразованный к схеме Pydantic (self.schema):
              [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16)]
            - ошибку sqlalchemy.orm.exc.MultipleResultsFound, если более одного результата.
            - None если результатов нет.
        """
        if pydantic_schema is None:
            pydantic_schema = self.schema

        if query is None:
            query = sa_select(self.model)
        query = query.filter_by(**filtering)

        result = await self.session.execute(query)

        # model = result.scalars().one_or_none()
        # if model is None:
        #     return None
        # return self.schema.model_validate(model)

        result = result.scalars().one_or_none()
        # result: None или <src.models.hotels.HotelsORM object at 0x0000023FB96EAD90>
        # one_or_none() чтобы вернуть первую строку результата или None
        # если результатов нет, или вызвать исключение exc.MultipleResultsFound,
        # если есть более одного результата.

        # Шаг 4: Преобразование объекта SQLAlchemy в Pydantic
        if result:
            # result_pydantic_schema = self.schema.model_validate(result, from_attributes=True)
            # result_pydantic_schema = self.schema.model_validate(result)
            result_pydantic_schema = pydantic_schema.model_validate(result)
            # К примеру, для отелей получаем элемент
            # HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16).
            # Тип возвращаемого элемента преобразован к схеме Pydantic:
            # self.schema или к схеме, переданной в параметре pydantic_schema.
            return result_pydantic_schema
        return None

