from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.exc import MultipleResultsFound

from src.api.dependencies.dependencies import pagination_pages
from src.repositories.base import BaseRepository, BaseRepositoryMyCode
from src.models.hotels import HotelsORM


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

    def __init__(self, session):
        super().__init__(session, HotelsORM)

    async def get_all(self):
        """
        Метод класса. Выбирает все строки. Использует родительский метод get_rows.
        """
        result = await super().get_rows(show_all=True)
        # Возвращает пустой список: [] или
        # [<src.models.hotels.HotelsORM object at 0x0000017FDD7C7810>,
        #  <src.models.hotels.HotelsORM object at 0x0000017FDD667C50>,
        #  ..., <src.models.hotels.HotelsORM object at 0x0000017FDD7C7890>]
        return result

    async def get_limit(self,
                        title=None,
                        location=None,
                        limit=pagination_pages["per_page"],
                        offset=pagination_pages["page"],
                        ):
        """
        Метод класса. Выбирает заданное количество строк с
        заданным смещением. Использует родительский метод get_rows.
        """
        query = select(self.model)
        if title:
            query = query.filter(func.lower(self.model.title)
                                 .contains(title.strip().lower()))
        if location:
            query = query.filter(func.lower(self.model.location)
                                 .contains(location.strip().lower()))
        result = await super().get_rows(query=query, limit=limit, offset=offset)
        # Возвращает пустой список: [] или
        # [<src.models.hotels.HotelsORM object at 0x0000017FDD7C7810>,
        #  <src.models.hotels.HotelsORM object at 0x0000017FDD667C50>,
        #  ..., <src.models.hotels.HotelsORM object at 0x0000017FDD7C7890>]
        return result

    async def get_one_or_none(self, title=None, location=None):
        """
        Метод класса. Возвращает одну строку или None. Если получено более
        одной строки, то поднимается исключение MultipleResultsFound.
        Использует родительский метод get_rows.
        """
        query = select(self.model)
        if title:
            query = query.filter(func.lower(HotelsORM.title)
                                 .contains(title.strip().lower()))
        if location:
            query = query.filter(func.lower(HotelsORM.location)
                                 .contains(location.strip().lower()))
        result = await super().get_rows(query=query, limit=2, offset=0)
        # Возвращает пустой список: [] или
        # [<src.models.hotels.HotelsORM object at 0x000001A9C4DF4090>]
        # В случае, если возвращается два экземпляра:
        # [<src.models.hotels.HotelsORM object at 0x000001A9C4DF4090>,
        #  <src.models.hotels.HotelsORM object at 0x000001A9C4DF4090>]
        # то требуется поднять ошибку MultipleResultsFound.
        # Так написано в документации: method sqlalchemy.engine.Result.one_or_none()
        # https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Result.one_or_none
        if len(result) > 1:
            raise MultipleResultsFound
        return result if result else None

    async def add(self, added_data: BaseModel, **kwargs):
        """
        Метод класса. Добавляет один объект в базу, используя метод
        insert. Возвращает номер добавленного объекта. Служит обёрткой
        для родительского метода add_item_insert.

        Возвращает добавленный объект.
        """
        result = await super().add(added_data, **kwargs)
        return result

    async def edit(self, edited_data: BaseModel, **filtering):  # -> None:
        result = await super().edit(edited_data, **filtering)
        return result


# HotelsRepository = HotelsRepositoryLesson
HotelsRepository = HotelsRepositoryMyCode
