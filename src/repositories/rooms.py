from typing import Union

from pydantic import BaseModel
from sqlalchemy import select, func, insert

from src.repositories.base import BaseRepository

from src.models.rooms import RoomsORM
from src.schemas.rooms import RoomPydanticSchema


class RoomsRepositoryMyCode(BaseRepository):
    model = RoomsORM
    schema = RoomPydanticSchema

    # Надо сделать обработку URL:
    # 1. Вывести информацию по всем номерам отеля
    # 2. Выбрать инфо по конкретному номеру по id
    # 3. Добавить номер с примерами данных
    # 4. Изменять номер post
    # 5. Изменять номер patch
    # 6. Удалять номер

    async def get_all(self, hotel_id):
        """
        Метод класса. Выбирает все строки. Использует родительский метод get_rows.

        :param query: SQL-Запрос. Если простой SELECT-запрос на выборку,
            то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :param hotel_id: Идентификатор отеля

        :return: Возвращает пустой список: [] или список из выбранных строк:
        [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
         HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
         ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
        Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        """
        query = select(self.model).filter_by(hotel_id=hotel_id)
        result = await super().get_rows(query=query,
                                        show_all=True)
        # Возвращает пустой список: [] или список:
        # [RoomPydanticSchema(hotel_id=16, title='title_string_1',
        #                     description='description_string_1', price=2, quantity=3, id=3),
        #  RoomPydanticSchema(hotel_id=16, title='title_string_2',
        #                     description='description_string_2', price=21, quantity=31, id=6)]
        #  ...,
        #  RoomPydanticSchema(hotel_id=16, title='title_string_N',
        #                     description='description_string_N', price=23, quantity=33, id=7)]
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        status = ("Полный список номеров для выбранного отеля.",
                  f"Всего выводится {len(result)} элемент(-а/-ов) на странице.")
        return status, ("Данные отсутствуют." if len(result) == 0 else result)

    async def get_id(self, room_id: Union[int | None] = None):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (поле self.model.id) один
        объект в базе, используя метод get. Служит обёрткой для родительского
        метода get_id.

        :param room_id: Идентификатор выбираемого объекта.

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
        if room_id is None:
            status = f"Не указан идентификатор комнаты для выборки"
            err_type = 2
            return {"status": status, "err_type": err_type, "got row": None}

        # result = await self.session.get(self.model, object_id)
        result = await super().get_id(room_id)
        # result: None или <src.models.hotels.HotelsORM object at 0x0000023FB96EAD90>
        # Возвращает пустой список: [] или объект:
        # HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16)
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        if not result:
            status = f"Для комнаты с идентификатором {room_id} ничего не найдено"
            err_type = 1
            return {"status": status, "err_type": err_type, "got row": None}
        status = "OK"
        err_type = 0
        return {"status": status, "err_type": err_type, "got row": result}

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
            status = f"Не найден(ы) номер(а) для удаления"
            err_type = 1
            return {"status": status, "err_type": err_type, "deleted rows": None}
        status = "OK"
        err_type = 0
        return {"status": status, "err_type": err_type, "deleted rows": result}

    async def delete_id(self, room_id: int):  # -> None:
        """
        Метод класса. Выбирает по идентификатору (по первичному ключу) -
        поле self.model.id один объект в базе, используя метод get, удаляет
        методом session.delete.
        Используются методы:
        - session.get(RoomsORM, id) для получения объекта по ключу
        - session.delete(room_object) для удаления объекта room_object.
        Служит обёрткой для родительского метода delete.

        :param room_id: Идентификатор выбираемого объекта.
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
        result = await super().delete_id(object_id=room_id)
        if result is None:
            status = f"Для номера с идентификатором {room_id} ничего не найдено"
            err_type = 1
            return {"status": status, "err_type": err_type, "deleted rows": None}
        # Другой вариант:
        # result = await super().delete_id(object_id=room_id)
        # if len(result) == 0:
        #     status = f"Для номера с идентификатором {room_id} ничего не найдено"
        #     err_type = 1
        #     return {"status": status, "err_type": err_type, "deleted rows": None}
        status = "OK"
        err_type = 0
        return {"status": status, "err_type": err_type, "deleted rows": result}

    async def edit_id(self,
                      edited_data: BaseModel,
                      room_id=None,
                      exclude_unset: bool = False
                      ):  # -> None:
        """
        Метод класса. Редактирует один объект в базе, выбирая по
        идентификатору (по первичному ключу) - поле self.model.id
        один объект в базе, используя метод get.
        Служит обёрткой для родительского метода edit.

        :param edited_data: Новые значения для внесения в выбранную запись.
        :param room_id: Идентификатор выбираемого объекта.
        :param exclude_unset: Редактировать все поля модели (True) или
            редактировать только те поля, которым явно присвоено значением
            (даже если присвоили None).

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
        result = await super().edit_id(edited_data=edited_data,
                                       object_id=room_id,
                                       exclude_unset=exclude_unset)
        if result is None:
            status = f"Для номера с идентификатором {room_id} ничего не найдено"
            err_type = 1
            return {"status": status, "err_type": err_type, "updated rows": None}
        # Другой вариант:
        # result = await super().edit(edited_data=edited_data,
        #                             id=room_id,
        #                             exclude_unset=exclude_unset)
        # if len(result) == 0:
        #     status = f"Для номера с идентификатором {room_id} ничего не найдено"
        #     err_type = 1
        #     return {"status": status, "err_type": err_type, "updated rows": None}
        status = "OK"
        err_type = 0
        return {"status": status, "err_type": err_type, "updated rows": result}

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
            status = f"Для номера с идентификатором {filtering['id']} ничего не найдено"
            err_type = 1
            return {"status": status, "err_type": err_type, "updated rows": None}
        status = "OK"
        err_type = 0
        return {"status": status, "err_type": err_type, "updated rows": result}


RoomsRepository = RoomsRepositoryMyCode
