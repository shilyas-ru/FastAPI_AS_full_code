from sqlalchemy import select, insert

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
                       **kwargs):
        """
        Выбирает заданное количество строк с заданным смещением.
        Возвращает список из выбранных строк или пустой список6 []
        """
        if query is None:
            query = select(self.model)
        if not show_all:
            query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def add_item_insert(self, **kwargs):
        """
        Метод класса. Добавляет один объект в базу, используя метод
        insert.
        Возвращает номер добавленного объекта.
        """
        add_stmt = insert(self.model).returning(self.model.id).values(**kwargs)
        result = await self.session.execute(add_stmt)
        return result.scalars().all()

    async def add_item(self, **kwargs):
        """
        Метод класса. Добавляет один объект в базу, используя метод
        session.add.
        Возвращает добавленный объект.
        После выполнения session.commit() возвращённый объект
        записывается в базу данных и получает значение в поле id.
        """
        new_item = self.model(**kwargs)
        self.session.add(new_item)
        return new_item


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
