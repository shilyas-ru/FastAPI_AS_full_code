from typing import Union

from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel

from src.api.dependencies.dependencies import pagination_pages
from src.database import engine


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
# В уроке назывался class BaseRepository:
class BaseRepositoryMyCode:
    model = None

    def __init__(self, session, model):
        self.session = session
        self.model = model

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
        :return: Возвращает список из выбранных строк или пустой список: []
        """
        if query is None:
            query = select(self.model)

        if not show_all:
            query = query.limit(limit).offset(offset)

        if order_by:
            query = query.order_by(self.model.id)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def add(self, added_data: BaseModel, **kwargs):
        """
        Метод класса. Добавляет один объект в базу, используя метод insert.

        :param added_data: Добавляемые данные.
        :param kwargs: Возможные иные именованные аргументы (не используются).
        :return: Возвращает список, содержащий добавленный объект.
        """
        add_stmt = (insert(self.model)
                    .returning(self.model)
                    .values(**added_data.model_dump()
                            )
                    )
        result = await self.session.execute(add_stmt)
        return result.scalars().all()

    async def edit(self,
                   edited_data: BaseModel,
                   exclude_unset: bool = False,
                   **filtering):  # -> None:
        """
        Метод класса. Редактирует один объект в базе, используя метод update.

        :param edited_data: Новые значения для внесения в выбранную запись.
        :param exclude_unset: Редактировать все поля модели (True) или
               редактировать только те поля, которым явно присвоено значением
               (даже если присвоили None).
        :param filtering: Значения фильтра для выбирания объекта.

        :return: Возвращает объект sqlalchemy.engine.result.ChunkedIteratorResult.
               Для получения конкретного объекта требуется сделать, например,
               оператор result.scalars().all().
        """
        edit_stmt = (update(self.model)
                     .filter_by(**filtering)
                     .values(**edited_data.model_dump(exclude_unset=exclude_unset))
                     .returning(self.model)
                     )
        print(edit_stmt.compile(compile_kwargs={"literal_binds": True}))
        # UPDATE hotels SET title='New_string', location='New_string' WHERE hotels.id = 188 RETURNING hotels.id, hotels.title, hotels.location
        # UPDATE hotels SET title='New_string', location='New_string' WHERE hotels.id = 198 RETURNING hotels.id, hotels.title, hotels.location
        result = await self.session.execute(edit_stmt)
        # result = <sqlalchemy.engine.result.ChunkedIteratorResult object at 0x000001ACD607BED0>
        # Если используется .returning(...), то тогда количество строк находится в:
        #   updated_rows = result.raw.rowcount
        # Если не используется .returning(...), то тогда количество строк находится в:
        #   updated_rows = result.rowcount
        return result

    async def delete(self, **filtering):  # -> None:
        """
        Метод класса. Удаляет один объект в базе, используя метод delete.

        :param filtering: Значения фильтра для выбирания объекта.
        :return: Возвращает объект sqlalchemy.engine.result.ChunkedIteratorResult.
               Для получения конкретного объекта требуется сделать, например,
               оператор result.scalars().all().
        """
        delete_stmt = delete(self.model).filter_by(**filtering).returning(self.model)
        # print(delete_stmt.compile(compile_kwargs={"literal_binds": True}))
        # DELETE FROM hotels WHERE hotels.id = 188 RETURNING hotels.id, hotels.title, hotels.location

        result = await self.session.execute(delete_stmt)
        # result = <sqlalchemy.engine.result.ChunkedIteratorResult object at 0x000002330C349350>
        # Если используется .returning(...), то тогда количество строк находится в:
        #   updated_rows = result.raw.rowcount
        # Если не используется .returning(...), то тогда количество строк находится в:
        #   updated_rows = result.rowcount
        # deleted_rows = result.raw.rowcount
        return result

    async def get_id(self, object_id: Union[int | None] = None):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (поле self.model.id) один
        объект в базе, используя метод get.

        :param object_id: Идентификатор выбираемого объекта.
        :return: Возвращает объект sqlalchemy.engine.result.ChunkedIteratorResult.
               Для получения конкретного объекта требуется сделать, например,
               оператор result.scalars().all().
        """
        result = await self.session.get(self.model, object_id)
        return result


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
