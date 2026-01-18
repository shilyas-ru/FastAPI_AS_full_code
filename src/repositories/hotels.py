from typing import Union

from pydantic import BaseModel
from sqlalchemy import select, func, delete
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
        Возвращает список из выбранных строк или пустой список: []
        """
        result = await super().get_rows(show_all=True)
        # Возвращает пустой список: [] или
        # [<src.models.hotels.HotelsORM object at 0x0000017FDD7C7810>,
        #  <src.models.hotels.HotelsORM object at 0x0000017FDD667C50>,
        #  ..., <src.models.hotels.HotelsORM object at 0x0000017FDD7C7890>]
        status = ("Полный список отелей.",
                  f"Всего выводится {len(result)} элемент(-а/-ов) на странице.")
        # if len(result) == 0:
        #     function_output = (status, f"Данные отсутствуют.")
        # else:
        #     function_output = (status, result)
        return status, ("Данные отсутствуют." if len(result) == 0 else result)

    async def get_limit(self,
                        title=None,
                        location=None,
                        per_page=pagination_pages["per_page"],
                        page=pagination_pages["page"],
                        ):
        """
        Метод класса. Выбирает заданное количество строк с
        заданным смещением. Использует родительский метод get_rows.

        :param title: Наименование отеля
        :param location: Адрес отеля
        :param per_page: Количество элементов на странице (должно быть >=1 и <=30, по умолчанию значение 3).
        :param page: Номер страницы для вывода (должно быть >=1, по умолчанию значение 1).
        :return:
        # Возвращает пустой список: [] или
        # [<src.models.hotels.HotelsORM object at 0x0000017FDD7C7810>,
        #  <src.models.hotels.HotelsORM object at 0x0000017FDD667C50>,
        #  ..., <src.models.hotels.HotelsORM object at 0x0000017FDD7C7890>]
        """
        # """
        # Возвращает список из выбранных строк или пустой список: []
        # """
        query = select(self.model)
        if title:
            query = query.filter(func.lower(self.model.title)
                                 .contains(title.strip().lower()))
        if location:
            query = query.filter(func.lower(self.model.location)
                                 .contains(location.strip().lower()))
        result = await super().get_rows(query=query,
                                        limit=per_page,
                                        offset=((page - 1) * per_page)
                                        )
        # Возвращает пустой список: [] или
        # [<src.models.hotels.HotelsORM object at 0x0000017FDD7C7810>,
        #  <src.models.hotels.HotelsORM object at 0x0000017FDD667C50>,
        #  ..., <src.models.hotels.HotelsORM object at 0x0000017FDD7C7890>]
        status = (f'Страница {pagination_pages["page"]}, установлено отображение '
                  f'{pagination_pages["per_page"]} элемент(-а/-ов) на странице.',
                  f"Всего выводится {len(result)} элемент(-а/-ов) на странице.")
        # if len(result) == 0:
        #     function_output = (status, f"Данные отсутствуют.")
        # else:
        #     function_output = (status, result)
        return status, ("Данные отсутствуют." if len(result) == 0 else result)

    async def get_one_or_none(self,
                              title=None,
                              location=None,
                              ):
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
                   exclude_unset: bool = False,
                   **filtering):  # -> None:
        """
        Метод класса. Редактирует один объект в базе, используя метод
        update. Служит обёрткой для родительского метода edit.

        :param edited_data: Новые значения для внесения в выбранную запись.
        :param exclude_unset: Редактировать все поля модели (True) или
               редактировать только те поля, которым явно присвоено значением
               (даже если присвоили None).
        :param filtering: Значения фильтра для выбирания объекта.

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
        result = await super().edit(edited_data, exclude_unset, **filtering)
        # Если используется .returning(...), то тогда количество строк находится в:
        #   updated_rows = result.raw.rowcount
        # Если не используется .returning(...), то тогда количество строк находится в:
        #   updated_rows = result.rowcount
        updated_rows = result.raw.rowcount
        if updated_rows == 0:
            status = f"Для отеля с идентификатором {filtering['id']} ничего не найдено"
            err_type = 1
            return {"status": status, "err_type": err_type, "updated rows": None}
        status = "OK"
        err_type = 0
        return {"status": status, "err_type": err_type, "updated rows": result.scalars().all()}

    async def delete(self, **filtering):  # -> None:
        """
        Метод класса. Удаляет один объект в базе, используя метод
        delete.

        :param filtering: Значения фильтра для выбирания объекта.
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
        result = await super().delete(**filtering)
        # Если используется .returning(...), то тогда количество строк находится в:
        #   updated_rows = result.raw.rowcount
        # Если не используется .returning(...), то тогда количество строк находится в:
        #   updated_rows = result.rowcount
        deleted_rows = result.raw.rowcount
        if deleted_rows == 0:
            status = f"Для отеля с идентификатором {filtering['id']} ничего не найдено"
            err_type = 1
            return {"status": status, "err_type": err_type, "deleted rows": None}
        status = "OK"
        err_type = 0
        return {"status": status, "err_type": err_type, "deleted rows": result.scalars().all()}

    async def get_id(self, object_id: Union[int | None] = None):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (поле self.model.id) один
        объект в базе, используя метод get.

        :param object_id: Идентификатор выбираемого объекта.

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
        if object_id is None:
            status = f"Не указан идентификатор отеля для выборки"
            err_type = 2
            return {"status": status, "err_type": err_type, "got row": None}

        result = await self.session.get(self.model, object_id)
        # result = <src.models.hotels.HotelsORM object at 0x00000277F9D5BD50>
        if not result:
            status = f"Для отеля с идентификатором {object_id} ничего не найдено"
            err_type = 1
            return {"status": status, "err_type": err_type, "got row": None}
        status = "OK"
        err_type = 0
        return {"status": status, "err_type": err_type, "got row": result}


# HotelsRepository = HotelsRepositoryLesson
HotelsRepository = HotelsRepositoryMyCode
