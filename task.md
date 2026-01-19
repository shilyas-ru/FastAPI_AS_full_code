## Задание № 16: Изменение удобств номера через API

Необходимо вместе с редактирование номеров через PUT и PATCH дать 
возможность редактировать удобства номера.

То есть новых ручек создавать не нужно — все задание решается 
внутри уже существующих ручек на изменение номера.

Звучит просто. Но на деле всё сложнее. У номера уже могут быть 
какие-то удобства, например, с айдишниками 1 и 2. А пользователь 
решил убрать удобство 1 и добавить удобство 3.

Теперь, нам как бэкендерам, необходимо удалить из m2m таблицы 
удобство 1 и добавить удобство 3. В идеале оставить удобство 2 
нетронутым, чтобы:

1. Запросы происходили быстрее (т.к. часть данных не изменяется).
2. Столбец id не рос слишком быстро. А то может случиться так, 
   что он превысит лимит и нам придется тратить память, чтобы 
   увеличить лимит столбца id (речь про тип bigint в PostgreSQL).


Задача в том, чтобы придумать рабочий способ определения тех удобств, 
которые нуждаются в удалении или добавлении. И произвести манипуляции 
вставки или удаления только с ними. А нетронутые удобства оставить 
нетронутыми.


## Что сделано

К заданию № 15 "Задание № 15: Получение и добавление удобств"
добавлено:

- Добавляем работу с таблицей `rooms_facilities` (таблица `many-to-many`).
- Добавляем данные в таблицу `rooms_facilities` (модель `RoomsFacilitiesORM` 
  в файле src\models\facilities.py). Делаем, чтобы при добавлении нового 
  номера можно было сразу добавить список удобств, находящихся в этом 
  номере:
    - В схеме номеров (файл src\schemas\rooms.py) в Pydantic-схемах, 
      которые обеспечивают получение данных с сайта (схемы в имени которых 
      присутствует `Request`, применяемые для организации query и body 
      параметров) добавляем поле - список из идентификаторов удобств:
        - В class `RoomDescrRecRequest(BaseModel)` добавляем:
            - поле: `facilities_ids: list[int]`
        - В class `RoomDescrOptRequest(BaseModel)` добавляем:
            - поле: `facilities_ids: list[int] | None = None`
    - Делаем Pydantic-схемы для отношения `rooms_facilities`.<br>
      В файле src\schemas\facilities.py для схем. В нём создаём нужные схемы:
        - `class RoomsFacilityBase(BaseModel)`.
        - `class RoomsFacilityPydanticSchema(FacilityBase)`.
    - Делаем репозиторий. В файле src\repositories\facilities.py, 
      создаём:
        - Создали класс `class RoomsFacilitiesRepository(BaseRepository)` с 
          атрибутами:
            - `model = RoomsFacilitiesORM`.
            - `schema = RoomsFacilityPydanticSchema`.
        - Создали метод класса:
            - `set_facilities_in_rooms_values`.
    - Добавляем в src\utils\db_manager.py:
        - В методе `async def __aenter__` добавляем:<br>
          `self.rooms_facilities = RoomsFacilitiesRepository(self.session)`.
    - Добавляем в файле src\repositories\base.py в базовом репозитории 
      `BaseRepository` метод `add_bulk` для создания сразу многих данных.
    - Добавляем информацию о `facilities` в примеры `openapi_examples_dict` в 
      файле src\api\routers\rooms.py.
    - Редактируем в файле src\api\routers\rooms.py функцию для создания
      номеров: `create_room_post`, добавляя указанные удобства в таблицу 
      `rooms_facilities`.
- Добавляем в методы изменения информации о номере возможность добавлять, 
  редактировать и удалять информацию об удобствах:
    - Изменяем репозиторий. В файле src\repositories\facilities.py в
      классе `RoomsFacilitiesRepository` создаём метод для обработки 
      списка удобств: `set_facilities_in_rooms_values`.
    - Редактируем в файле src\api\routers\rooms.py функции для изменения 
      информации о номере:
        - `change_room_put`,
        - `change_room_hotel_id_put`,
        - `change_room_patch`,
        - `change_room_hotel_id_patch`.

## Итог

- Структура проекта (см. файл "[project_structure.md](project_structure.md)").

- Созданные таблицы в базе данных см. картинку "[tables_in_database.png](tables_in_database.png)".

- Краткая справка по командам alembic - см. файл "[src/models/ReadMe.md](src/models/ReadMe.md)".

- Используемые сокращения и именования переменных/классов/прочего - см. файл [variables_abbreviations_and_naming.md](variables_abbreviations_and_naming.md)