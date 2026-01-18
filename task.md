## Задание №9: Получение cookie пользователя внутри ручки

Необходимо реализовать получение токена access_token из cookie пользователя, которые отправляет браузер. Внутри cookie может либо находится наш токен, либо будет пусто (если юзер не аутентифицирован).

Цель задания — открыть для себя мир исходного кода библиотек, с которыми вы работаете. Взглянуть на код, который пишут продвинутые Python разработчики (см. [скриншот](Screenshot_at_Aug_28_23-55-56.png)), а также переписать ручки PUT и DELETE.

***Скриншот:***<br>
<img src="https://github.com/shilyas-ru/FastAPI_AS/blob/main/10-User_authorization_and_authentication-Receiving_user_cookies/Screenshot_at_Aug_28_23-55-56.png" alt="скриншот" height="135">


*Код со [скриншота](Screenshot_at_Aug_28_23-55-56.png):*
```
@router.get("/only_auth")
async def only_auth(
        request: Request,
):
    ...
    access_token = "..." or None
```


## Уведомления

- Требуется создать в корне проекта файл `.env` и заполнить значения, указанные в файле `.env`:
```
DB_HOST=
DB_PORT=
DB_USER=
DB_PASS=
DB_NAME=

JWT_SECRET_KEY=
JWT_ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
```
Пример заполнения данных (указывается только по причине того, что проект учебный!!!), так же см. файл [.env-example](.env-example):
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=booking

JWT_SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```


## Что сделано

К заданию №8 "Задание №8: Запретить создание нескольких юзеров с одинаковой почтой" добавлено:

- Создан роутер для работы с пользователями (см. файл "[src/api/routers/auth.py](src/api/routers/auth.py)"), написана обработка:
    - post("/auth/login") - Проверка, что пользователь существует и может 
        авторизоваться.<br>
        Функция: login_user_post
    - post("/auth/register") - Создание записи с новым пользователем.<br>
        Функция: register_user_post
    - post("/auth/only_auth") - Тестовый метод для получения куков по имени 
        (в примере проверяется значение для access_token).<br>
        Функция: only_auth

- Создан файл для работы с токенами, авторизацией, хешированием паролей и т.д. (см. файл "[src/services/auth.py](src/services/auth.py)"), используется в "[src/api/routers/auth.py](src/api/routers/auth.py)"


Рабочие ссылки (список методов, параметры в подробном перечне):
- post("/auth/login") - Проверка, что пользователь существует и может 
    авторизоваться.<br>
    Функция: login_user_post
- post("/auth/register") - Создание записи с новым пользователем.<br>
    Функция: register_user_post
- post("/auth/only_auth") - Тестовый метод для получения куков по имени 
    (в примере проверяется значение для access_token).<br>
    Функция: only_auth


## Итог

- Структура проекта (см. файл "[project_structure.md](project_structure.md)").

- Созданные таблицы в базе данных см. картинку "[tables_in_database.png](tables_in_database.png)".

- Краткая справка по командам alembic - см. файл "[src/models/ReadMe.md](src/models/ReadMe.md)".

- Используемые сокращения и именования переменных/классов/прочего - см. файл [variables_abbreviations_and_naming.md](variables_abbreviations_and_naming.md)