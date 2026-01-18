## Задание №11: Функционал номеров
Необходимо создать API ручки для взаимодействия с номерами. По сути, 
нужны все те же самые ручки, что мы делали для отелей (см. [скриншот](https://github.com/shilyas-ru/FastAPI_AS/blob/main/12-Database-Rooms_functionality/Screenshot_at_Aug_29_01-19-03.png)).

Для этого нужны создать:
- роутер и ручки
- pydantic схемы
- репозиторий

Давайте вынесем роутер с номерами в отдельный файл, чтобы 
файл hotels.py не сильно распух :)

Конкретизировано в видео:
- Именование URL: /hotels/{hotel_id}/rooms/{rooms_id}
- Необходимо реализовать для номеров:
    1. Вывести информацию по всем номерам отеля
    2. Выбрать инфо по конкретному номеру по id
    3. Добавить номер с примерами данных
    4. Изменять номер post
    5. Изменять номер patch
    6. Удалять номер


***Скриншот:***<br>
<img src="https://github.com/shilyas-ru/FastAPI_AS/blob/main/12-Database-Rooms_functionality/Screenshot_at_Aug_29_01-19-03.png" alt="скриншот" height="270">


*Код со [скриншота](https://github.com/shilyas-ru/FastAPI_AS/blob/main/12-Database-Rooms_functionality/Screenshot_at_Aug_29_01-19-03.png):*
```
get("/hotels") - Get Hotels
post("/hotels") - Create Hotels
get("/hotels/{hotel_id}") - Get Hotel
put("/hotels/{hotel_id}") - Edit Hotel
patch("/hotels/{hotel_id}") - Частичное обновление данных об отеле
delete("/hotels/{hotel_id}") - Delete Hotel
```



## Что сделано

К заданию №10: "Задание №10: Ручка на выход из системы" добавлено:

- Добавлено:
    - В базовом репозитории BaseRepositoryMyCode добавлен метод delete_id. Метод класса. Выбирает по идентификатору 
      (по первичному ключу) - поле self.model.id один объект в базе, используя метод get, удаляет методом session.delete.<br>
      Используются методы:
        - session.get(RoomsORM, object_id) для получения объекта по ключу
        - session.delete(room_object) для удаления объекта room_object.
        
    - Сделан репозитарий RoomsRepositoryMyCode, дочерний к базовому репозитарию BaseRepositoryMyCode (см. файл "[src/repositories/rooms.py](src/repositories/rooms.py)").

    - Сделана обработка эндпоинтов для номеров (см. файл "[src/api/routers/rooms.py](src/api/routers/rooms.py)").


Рабочие ссылки (список методов, параметры в подробном перечне):
- post("/hotels/room") - Создание записи с новой комнатой в отеле.
- get("/hotels/{hotel_id}/rooms") - Вывод списка номеров для конкретного 
        отеля - весь список полностью.
- get("/hotels/rooms/{room_id}") - Получение из базы данных выбранной 
        записи по идентификатору отеля.
- delete("/hotels/rooms/{room_id}") - Удаление выбранной записи по 
        идентификатору номера.<br>
        Реализовано удаление одного объекта, когда объект для удаления получаем 
        по первичному ключу (метод session.get), удаляем методом session.delete.<br>
        Используются методы:
    - session.get(RoomsORM, id) для получения объекта по ключу
    - session.delete(room_object) для удаления объекта room_object.
- delete("/hotels/rooms/") - Удаление выбранной записи по 
        идентификатору номера.<br>
        При желании можно дополнить удаление по любым условиям, а не только по id.
        Удаление выбранных записей реализовано через метод delete.
- put("/hotels/rooms/{room_id}") - Обновление ВСЕХ данных одновременно 
        для выбранной записи, выборка происходит по идентификатору номера.
- patch("/hotels/rooms/{room_id}") - Обновление каких-либо данных выборочно 
        или всех данных сразу для выбранной записи, выборка происходит по 
        идентификатору номера.


## Итог

- Структура проекта (см. файл "[project_structure.md](project_structure.md)").

- Созданные таблицы в базе данных см. картинку "[tables_in_database.png](tables_in_database.png)".

- Краткая справка по командам alembic - см. файл "[src/models/ReadMe.md](src/models/ReadMe.md)".

- Используемые сокращения и именования переменных/классов/прочего - см. файл [variables_abbreviations_and_naming.md](variables_abbreviations_and_naming.md)