from typing import Union

from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel

from src.api.dependencies.dependencies import pagination_pages
# from src.database import engine

# engine нужен, чтобы использовать диалект SQL:
# add_stmt = (insert(self.model)
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

# from src.schemas.hotels import HotelPydanticSchema


# BaseRepositoryLesson - код репозитария из урока.
# В уроке назывался class BaseRepository:
class BaseRepositoryLesson:
    model = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def add(self, data: BaseModel):
        add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(add_data_stmt)
        return result.scalars().one()

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(update_stmt)

    async def delete(self, **filter_by) -> None:
        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)


# BaseRepositoryMyCode - мой код репозитария.
# В уроке назывался class BaseRepository

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

class BaseRepositoryMyCode:
    model = None
    schema: BaseModel = None

    # def __init__(self, session, model):
    #     self.session = session
    #     # self.model = model  # Атрибут экземпляра класса
    #     BaseRepositoryMyCode.model = model  # Атрибут класса

    def __init__(self, session):
        self.session = session

    async def get_rows(self, *args,
                       query=None,
                       offset=(pagination_pages["page"] - 1) * pagination_pages["per_page"],
                       limit=pagination_pages["per_page"],
                       show_all=None,
                       order_by=True,
                       **kwargs):
        """
        Метод выбирает заданное количество строк с заданным смещением.

        :param args: Возможные неименованные аргументы (не используются).
        :param query: SQL-Запрос. Если простой SELECT-запрос на выборку,
                то он формируется внутри метода. В качестве значений могут
                приходить запросы, связанные с разными фильтрами.
        :param offset: Количество строк, пропускаемых при выборке.
                Имеет значение по умолчанию.
                Не используется, если параметр show_all=True.
        :param limit: Количество строк, выбираемых из базы данных.
                Имеет значение по умолчанию.
                Не используется, если параметр show_all=True.
        :param show_all: Выбирать сразу (True) все записи, соответствующие
                запросу, или выполнить ограниченную выборку (False или None).
                Может отсутствовать.
        :param order_by: Упорядочивать перед выборкой по полю self.model.id
                записи, соответствующие запросу (True), или выбирать,
                основываясь на порядке в базе данных (False или None).
                Может отсутствовать.
        :param kwargs: Возможные иные именованные аргументы (не используются).
        :return: Возвращает пустой список: [] или список из выбранных строк:
                [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
                 HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
                 ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
                Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        """
        if query is None:
            query = select(self.model)

        if not show_all:
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
        # Чтобы это убрать, добавляем в модель
        result_pydantic_schema = [self.schema.model_validate(row_model,
                                                             from_attributes=True)
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
        # add_stmt = (insert(self.model)
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
        add_stmt = (insert(self.model)
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
        result_pydantic_schema = [self.schema.model_validate(row_model,
                                                             from_attributes=True)
                                  for row_model in result.scalars().all()]
        # return result.scalars().all()
        return result_pydantic_schema

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
               Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        """
        # edit_stmt = (update(self.model)
        #              .filter_by(**filtering)
        #              .values(**edited_data.model_dump(exclude_unset=exclude_unset))
        #              .returning(self.model)
        #              )
        if edit_stmt is None:
            edit_stmt = update(self.model)
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
        result_pydantic_schema = [self.schema.model_validate(row_model,
                                                             from_attributes=True)
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

        :return: Возвращает None или объект, преобразованный к схеме Pydantic: self.schema.
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
            result_pydantic_schema = self.schema.model_validate(result, from_attributes=True)
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
        :return: Возвращает объект sqlalchemy.engine.result.ChunkedIteratorResult.
            Для получения конкретного объекта требуется сделать, например,
            оператор result.scalars().all().
        """
        # delete_stmt = delete(self.model).filter_by(**filtering).returning(self.model)
        if delete_stmt is None:
            delete_stmt = delete(self.model)
        # print(delete_stmt.compile(compile_kwargs={"literal_binds": True}))
        delete_stmt = delete_stmt.filter_by(**filtering).returning(self.model)
        # print(delete_stmt.compile(compile_kwargs={"literal_binds": True}))
        # DELETE FROM hotels WHERE hotels.id = 188
        # RETURNING hotels.id, hotels.title, hotels.location

        result = await self.session.execute(delete_stmt)
        # result = <sqlalchemy.engine.result.ChunkedIteratorResult object at 0x000002330C349350>
        result_pydantic_schema = [self.schema.model_validate(row_model,
                                                             from_attributes=True)
                                  for row_model in result.scalars().all()]
        # Получаем пустой список: [] или список:
        # [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
        #  HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
        #  ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        # return result
        return result_pydantic_schema

    async def get_id(self, object_id: Union[int | None] = None):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (поле self.model.id) один
        объект в базе, используя метод get.

        :param object_id: Идентификатор выбираемого объекта.
        :return: Возвращает None или объект, преобразованный к схеме Pydantic: self.schema.
        """
        result = await self.session.get(self.model, object_id)
        # result: None или <src.models.hotels.HotelsORM object at 0x0000023FB96EAD90>
        # return result
        # Шаг 4: Преобразование объекта SQLAlchemy в Pydantic
        if result:
            result_pydantic_schema = self.schema.model_validate(result, from_attributes=True)
            # Получаем элемент HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16).
            # Тип возвращаемого элемента преобразован к схеме Pydantic: self.schema
            return result_pydantic_schema
        return None

    async def get_one_or_none(self, query=None):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (поле self.model.id) один
        объект в базе, используя метод get.

        :param query: SQL-Запрос. Если простой SELECT-запрос на выборку,
            то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :return: Возвращает первую строку результата или None если результатов нет,
            или вызывает исключение если есть более одного результата.
            - список, содержащий один элемент, преобразованный к схеме Pydantic (self.schema):
              [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16)]
            - ошибку sqlalchemy.orm.exc.MultipleResultsFound, если более одного результата.
            - None если результатов нет.
        """
        if query is None:
            query = select(self.model)
        result = await self.session.execute(query).scalars().one_or_none()
        # result: None или <src.models.hotels.HotelsORM object at 0x0000023FB96EAD90>
        # return result
        result = result.scalars().one_or_none()
        # one_or_none() чтобы вернуть первую строку результата или None
        # если результатов нет, или вызвать исключение если есть более одного результата.
        # Шаг 4: Преобразование объекта SQLAlchemy в Pydantic
        if result:
            result_pydantic_schema = self.schema.model_validate(result, from_attributes=True)
            # Получаем элемент HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16).
            # Тип возвращаемого элемента преобразован к схеме Pydantic: self.schema
            return result_pydantic_schema
        return None


# BaseRepository = BaseRepositoryLesson
BaseRepository = BaseRepositoryMyCode

# query = kwargs.get('query',
#                    select(BaseRepositoryMyCode.model))

# offset = (page - 1) * per_page
# offset = kwargs.get('offset',
#                     (pagination_pages["page"] - 1) * pagination_pages["per_page"])
# limit = per_page
# limit = kwargs.get('limit',
#                    pagination_pages["per_page"])

# show_all = kwargs.get('show_all', None)
