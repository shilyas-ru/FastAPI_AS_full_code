from fastapi import HTTPException

from pydantic import BaseModel
from sqlalchemy import func as sa_func

from sqlalchemy import select as sa_select  # Для реализации SQL команды SELECT
from sqlalchemy import delete as sa_delete  # Для реализации SQL команды DELETE
from sqlalchemy import update as sa_update  # Для реализации SQL команды UPDATE
from sqlalchemy import insert as sa_insert  # Для реализации SQL команды INSERT

from sqlalchemy import Select as sa_Select  # Тип функции sa_select
from sqlalchemy import Delete as sa_Delete  # Тип функции sa_delete
from sqlalchemy import Update as sa_Update  # Тип функции sa_update
from sqlalchemy import Insert as sa_Insert  # Тип функции sa_insert


from src.repositories.base import BaseRepository

from src.models.facilities import FacilitiesORM, RoomsFacilitiesORM
from src.schemas.facilities import FacilityPydanticSchema, RoomsFacilityPydanticSchema


# from src.database import engine
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

class FacilitiesRepository(BaseRepository):
    model = FacilitiesORM
    schema = FacilityPydanticSchema

    async def get_limit(self,
                        *filter,
                        query: sa_Select | None = None,
                        title: str | None = None,
                        per_page: int | None = None,
                        page: int | None = None,
                        show_all: bool | None = None,
                        **filter_by,
                        ):
        """
        Метод класса. Выбирает заданное количество строк с
        заданным смещением. Использует родительский метод get_rows.

        :param filter: Фильтры для запроса - конструкция .filter(*filter).
        :param query: SQL-Запрос. Если простой SELECT-запрос на выборку,
            то он формируется внутри метода. В качестве значений могут
            приходить запросы, связанные с разными фильтрами.
        :param title: Наименование удобства
        :param per_page: Количество элементов на странице (должно быть >=1 и
            <=30, по умолчанию значение 3).
        :param page: Номер страницы для вывода (должно быть >=1, по умолчанию
            значение 1).
        :param show_all: Выбирать сразу (True) все записи, соответствующие
                запросу, или выполнить ограниченную выборку (False или None).
                Может отсутствовать.
        :param filter_by: Фильтры для запроса - конструкция .filter_by(**filter_by).
        :return: Возвращает список:
            [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
             HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
             ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
            Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema

        Если элементы, соответствующие запросу на редактирование в параметре edit_stmt
        и фильтрам, указанным в **filtering, отсутствуют, возбуждается исключение
        HTTPException с кодом 404.
        """

        if query is None:
            query = sa_select(self.model)

        if title:
            query = query.filter(sa_func.lower(self.model.title)
                                 .contains(title.strip().lower()))
        result = await super().get_rows(*filter,
                                        query=query,
                                        per_page=per_page,
                                        page=page,
                                        show_all=show_all,
                                        **filter_by
                                        )
        # Возвращает пустой список: [] или список:
        # [HotelPydanticSchema(title='title_string_1', location='location_string_1', id=16),
        #  HotelPydanticSchema(title='title_string_2', location='location_string_2', id=17),
        #  ..., HotelPydanticSchema(title='title_string_N', location='location_string_N', id=198)]
        # Тип возвращаемых элементов преобразован к схеме Pydantic: self.schema
        if len(result) == 0:
            # status_code=404: Сервер понял запрос, но не нашёл
            #                  соответствующего ресурса по указанному URL
            raise HTTPException(status_code=404,
                                detail={"description": "Данные отсутствуют.",
                                        })
        if show_all:
            status = "Полный список удобств в номерах."
        else:
            status = (f'Страница {page}, установлено отображение '
                      f'{per_page} элемент(-а/-ов) на странице.')

        status = (status,
                  f"Всего выводится {len(result)} элемент(-а/-ов) на странице.")
        return {"status": status, "facilities": result}


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesORM
    schema = RoomsFacilityPydanticSchema

    async def set_facilities_in_rooms_values(self,
                                             room_id: int,
                                             facilities_ids: list[int]):
        get_facilities_ids_query = (sa_select(self.model.facility_id)
                                    .filter_by(room_id=room_id)
                                    )
        result = await self.session.execute(get_facilities_ids_query)
        current_facilities_ids = result.scalars().all()
        items_to_delete = list(set(current_facilities_ids) - set(facilities_ids))
        items_to_insert = list(set(facilities_ids) - set(current_facilities_ids))

        if items_to_delete:
            delete_facilities_from_room_stmt = (sa_delete(self.model)
                                                .filter(self.model.room_id == room_id,
                                                        self.model.facility_id.in_(items_to_delete),
                                                        )
                                                )
            await self.session.execute(delete_facilities_from_room_stmt)

        if items_to_insert:
            insert_facilities_in_room_stmt = (sa_insert(self.model)
                                              .values([{"room_id": room_id, "facility_id": f_id}
                                                       for f_id in items_to_insert]
                                                      )
                                              )
            await self.session.execute(insert_facilities_in_room_stmt)
