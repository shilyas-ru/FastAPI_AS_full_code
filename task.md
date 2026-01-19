## Задание № 17: Получение удобств конкретного номера

Необходимо получать удобства в ручке для получения конкретного номера.

Для этого необходимо создать новый метод в репозитории RoomsRepository, 
который подгрузит удобства через relationship, и вызвать этот метод внутри ручки.


## Что сделано

К заданию "Задание № 16: Изменение удобств номера через API"
добавлено:

- Добавляем `relationship` - получение связанных данных в одной модели.
    - В модели номеров (файл src\models\rooms.py) в класс `RoomsORM(Base)` 
      добавляем атрибут:
      - `rooms: Mapped[list["RoomsORM"]] = relationship(`<br>
        `                secondary="rooms_facilities",`<br>
        `                back_populates="facilities")`<br>
    - В модели удобств (файл src\models\facilities.py) в класс `FacilitiesORM(Base)` 
      добавляем атрибут:
      - `facilities: Mapped[list["FacilitiesOrm"]] = relationship(`<br>
        `                secondary="rooms_facilities",`<br>
        `                back_populates="rooms")`<br>
    - В обе модели добавляем импорт: 
        - `from sqlalchemy.orm import relationship`
    - Добавляем схему, учитывающую список удобств в номере. Редактируем файл
      src\schemas\rooms.py, добавляя:
        - `class RoomWithRels(RoomPydanticSchema):`<br>
          `    facilities: list[FacilityPydanticSchema]`<br>
    - Редактируем репозитарий `RoomsRepository` в файле src\repositories\rooms.py:
        - Правим метод `get_limit`, добавляя:
            - параметр: `pydantic_schema=None,`
            - код: <br>
              `if pydantic_schema is RoomWithRels:`<br>
              `    query = query.options(selectinload(self.model.facilities))`<br>
    - Редактируем репозитарий `BaseRepository` в файле src\repositories\base.py:
        - Правим метод `get_rows`:
            - Добавляя параметр: `pydantic_schema=None,`
            - Редактируя код: <br>
              `if pydantic_schema is None:`<br>
              `    pydantic_schema = self.schema`<br>
            - Редактируя код, заменив `self.schema.model_validate`
              на `pydantic_schema.model_validate`, итог:<br>
              `result_pydantic_schema = [pydantic_schema.model_validate(row_model)`<br>
              `                          for row_model in result.scalars().all()]`<br>
    - Редактируем ручку, в которой получаем все номера. для этого добавляем в 
      вызов метода `db.rooms.get_limit` параметр `pydantic_schema=RoomWithRels,` в
      функции:
        - `show_rooms_in_hotel_all_get`, ручка `get("/{hotel_id}/rooms/all")`.
        - `show_rooms_in_hotel_free_get`, ручка `get("/{hotel_id}/rooms/free")`.
    - Добавляем вывод удобств при получении конкретного номера. Номер можно 
      получить двумя вариантами: используя метод `session.get` или используя метод<br>
      `session.execute(select(model).filter_by(**filtering))`.
        - Переименовываем ручку `get("/rooms/{room_id}")`, функция `get_rooms_id_get`
          в `get("/rooms/{room_id}/session_get")`, функция `get_room_session_get_method_get`.
        - Добавляем ручку `get("/rooms/{room_id}/session_execute")`, функция
          `get_room_session_execute_method_get`.
        - В метод `get_id` в метод `get_by_id` файлах:
            - src\api\routers\auth.py
            - src\api\routers\bookings.py
            - src\api\routers\hotels.py
            - src\api\routers\rooms.py
            - src\repositories\base.py
            - src\repositories\hotels.py
            - src\repositories\rooms.py
        - Реализуем вариант с `session.get`. Для этого:
            - Редактируем в файле src\repositories\rooms.py в репозитарии 
              `RoomsRepository`:
                - Правим метод `get_by_id`, добавляя:
                    - Формируем запрос: `query = ...`
                    - Выполняем запрос: `result_m2m_room_facilities = ...`
                    - Преобразовываем полученный результат к схеме pydantic<br>
                      `result_pydantic_schema = [FacilityPydanticSchema...]`
                    - Объединяем полученные `result_m2m_room_facilities` и 
                      `result_pydantic_schema` в итоговый результат, преобразуя<br>
                      `result = RoomWithRels.model_validate(...)`
        - Реализуем вариант с `session.execute(select(model).filter_by(**filtering))`.
          Для этого:
            - Создаём в файле src\repositories\rooms.py в репозитарии 
              `RoomsRepository`:
                - `Метод get_by_id_one_or_none`

## Итог

- Структура проекта (см. файл "[project_structure.md](project_structure.md)").

- Созданные таблицы в базе данных см. картинку "[tables_in_database.png](tables_in_database.png)".

- Краткая справка по командам alembic - см. файл "[src/models/ReadMe.md](src/models/ReadMe.md)".

- Используемые сокращения и именования переменных/классов/прочего - см. файл [variables_abbreviations_and_naming.md](variables_abbreviations_and_naming.md)