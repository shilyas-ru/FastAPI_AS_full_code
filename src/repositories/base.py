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
        Выбирает заданное количество строк с заданным смещением.
        Возвращает список из выбранных строк или пустой список: []
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
        Метод класса. Добавляет один объект в базу, используя метод
        insert.

        Возвращает добавленный объект.
        """
        add_stmt = (insert(self.model)
                    .returning(self.model)
                    .values(**added_data.model_dump()
                            )
                    )
        result = await self.session.execute(add_stmt)
        f = result
        print(f)
        return result.scalars().all()

    async def edit(self, edited_data: BaseModel, **filtering):  # -> None:
        """
        Метод класса. Редактирует один объект в базе, используя метод
        update.

        Возвращает отредактированный объект.
        """
        edit_stmt = (update(self.model)
                     .filter_by(**filtering)
                     .values(**edited_data.model_dump())
                     .returning(self.model)
                     )
        # print(edit_stmt.compile(compile_kwargs={"literal_binds": True}))
        # UPDATE hotels SET title='New_string', location='New_string' WHERE hotels.id = 188 RETURNING hotels.id, hotels.title, hotels.location

        result = await self.session.execute(edit_stmt)
        # Если используется .returning(...), то тогда количество строк находится в:
        #   updated_rows = result.raw.rowcount
        # Если не используется .returning(...), то тогда количество строк находится в:
        #   updated_rows = result.rowcount
        updated_rows = result.raw.rowcount
        if updated_rows == 0:
            status = f"Для объекта с идентификатором {filtering['id']} ничего не найдено"
            err_type = 1
            return {"status": status, "err_type": err_type, "updated rows": None}
        status = "OK"
        err_type = 0
        return {"status": status, "err_type": err_type, "updated rows": result.scalars().all()}

    async def delete(self, **filtering):  # -> None:
        delete_stmt = delete(self.model).filter_by(**filtering).returning(self.model)
        # print(delete_stmt.compile(compile_kwargs={"literal_binds": True}))
        # DELETE FROM hotels WHERE hotels.id = 188 RETURNING hotels.id, hotels.title, hotels.location

        result = await self.session.execute(delete_stmt)
        # Если используется .returning(...), то тогда количество строк находится в:
        #   updated_rows = result.raw.rowcount
        # Если не используется .returning(...), то тогда количество строк находится в:
        #   updated_rows = result.rowcount
        deleted_rows = result.raw.rowcount
        if deleted_rows == 0:
            status = f"Для объекта с идентификатором {filtering['id']} ничего не найдено"
            err_type = 1
            return {"status": status, "err_type": err_type, "deleted rows": None}
        status = "OK"
        err_type = 0
        return {"status": status, "err_type": err_type, "deleted rows": result.scalars().all()}


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
