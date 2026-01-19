## Задание № 15: Получение и добавление удобств
Необходимо добавить роутер для удобств и две ручки:

    GET /facilities на получение всех удобств
    POST /facilities для добавления нового удобства

Обратите внимание, что пока мы не используем m2m таблицу. 
Она пригодится нам позже.


### Уведомление

Надо изменить базу данных и создать дополнительные таблицы, как указано в лекциях.


## Что сделано

К заданию № 14 "Задание № 14: Вернуть пагинацию и фильтрацию в получение отелей"
добавлено:

- Добавляем удобства (facilities) - это то, что предлагается в номере:
    - Создаём две таблицы в БД: facilities и rooms_facilities 
      (таблица many-to-many).<br>
      Для этого:
        - В папке с моделями (src\models) создаём файл с моделями facilities.py.<br>
          Создали модели:
            - `class FacilitiesORM(Base)`.
            - `class RoomsFacilitiesORM(Base)`.
        - Заходим в миграции (файл src\migration\env.py), импортируем какой-либо
          класс из файла с новой моделью (src\models\facilities.py).
        - Прогоняем миграции:<br>
          `alembic revision --autogenerate -m "006 Add facilities"`<br>
          Создан файл: 2025_02_07_0117-d63318ef9cad_006_add_facilities.py
        - Применяем все не обработанные миграции: `alembic upgrade head`
    - Реализуем две ручки для работы с удобствами (работаем с сущностью 
      FacilitiesORM из файла src\models\facilities.py): "Получать список
      удобств" и "Добавлять новое удобство".
      Для этого:
        - Делаем роутер. Создаём файл src\api\routers\facilities.py для 
          размещения кода для end-point'ов.
            - Делаем переменную с примерами:<br>
              `openapi_examples_dict`.
            - Делаем метод для создания удобств:<br>
              `create_facility_post`.
            - Делаем метод для вывода списка удобств:<br>
              `show_facilities_in_rooms_get`
        - Делаем Pydantic-схемы. Создаём файл src\schemas\facilities.py для 
          схем. В нём создаём нужные схемы:
            - `class FacilityDescriptionRecURL(BaseModel)`.
            - `class FacilityBase(BaseModel)`.
            - `class FacilityPydanticSchema(FacilityBase)`.
        - Делаем репозиторий. Создаём файл src\repositories\facilities.py, 
          создаём:
            - Создали класс class `FacilitiesRepository(BaseRepository)` с 
              атрибутами:
                - `model = FacilitiesORM`.
                - `schema = FacilityPydanticSchema`.
            - Создали метод класса:
                - `get_limit`.
        - Добавляем в src\utils\db_manager.py:
            - Добавляем импорт: <br>
              `from src.repositories.facilities import FacilitiesRepository`.
            - В методе `async def __aenter__` добавляем:<br>
              `self.facilities = FacilitiesRepository(self.session)`.
        - Редактируем файл src\main.py:
            - Добавляем импорт:<br>
              `from src.api.routers.facilities import router as router_facilities`.
            - Редактируем переменную `openapi_tags` - определяя параметры и 
              порядок вывода в документации.
            - Добавляем роутер:<br>
              `app.include_router(router_facilities)`.
    - Косметическая правка.<br>
      Обусловлено тем, что объекты для вывода сейчас не только отели.
        - В файле src\api\dependencies\dependencies.py в классе 
          `PaginationPagesAllParams` заменил наименование атрибута. 
        - Было: `PaginationPagesAllParams.all_hotels`.
        - Стало: `PaginationPagesAllParams.all_objects`.


## Итог

- Структура проекта (см. файл "[project_structure.md](project_structure.md)").

- Созданные таблицы в базе данных см. картинку "[tables_in_database.png](tables_in_database.png)".

- Краткая справка по командам alembic - см. файл "[src/models/ReadMe.md](src/models/ReadMe.md)".

- Используемые сокращения и именования переменных/классов/прочего - см. файл [variables_abbreviations_and_naming.md](variables_abbreviations_and_naming.md)