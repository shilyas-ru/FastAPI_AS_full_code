1. Инициировал папку для Alembic:
alembic init src\migration



2. Отредактировал файл alembic.ini в корне проекта.

2.1. Раздел [alembic]
В нём указан путь до папки с миграциями:
    script_location = src\migration


2.2. Надо добавить папки в параметре (разделять пробелом!!!)
Исходный параметр: prepend_sys_path = .

Делаю:
    prepend_sys_path = . src


3. Отредактировал файл src\migration\env.py.

3.1. В параметре target_metadata = None указываем наименование объекта с метаданными. 
В нашем случае это класс class Base(DeclarativeBase), описанный в файле database.py.
Получается так:
    target_metadata = Base.metadata
и добавляем импорт объекта Base:
    from src.database import Base

3.2. Добавляем импорт в файл после строки from src.database import Base:
    from src.models.hotels import HotelsORM
Это надо, чтобы метаданные из класса HotelsORM добавились в класс Base.

4. Переопределяю подключение SQLAlchemy к базе данных в файле alembic.ini в корне проекта.
Это переменная sqlalchemy.url = driver://user:pass@localhost/dbname
для этого в файле src\migration\env.py указываем:

4.1. перед строкой from src.database import Base добавляю строку:
    from src.config import settings
    
4.2. После строки config = context.config добавляю строку:
    config.set_main_option("sqlalchemy.url", f"{settings.DB_URL}?async_fallback=True")




---------------------- дополнение из инета -------------------
Поиск в яндексе по фразе "alembic async_fallback=True": https://ya.ru/search/?text=alembic+async_fallback%3DTrue&lr=65 дал результат:

Чтобы использовать Alembic в асинхронном режиме, нужно установить его сразу с параметром -t async. (1), (4) Для этого используется команда:

alembic init -t async <script_directory_here>

. (1), (2)

Также можно использовать URL-адрес базы данных с параметром «?async_fallback=True». Это запустит каждый метод DBAPI в новой асинхронной петле. (2)

Ещё один способ — прописать в файле env.py путь:

config.set_main_option("sqlalchemy.url", f"{DATABASE_URL}?async_fallback=True")

. (1)

После инициализации Alembic необходимо внести изменения в конфигурацию, чтобы корректно подключиться к базе данных и настроить форматирование миграций. (3)

ссылки:
 1: https://ru.stackoverflow.com/questions/1561339/Ошибка-асинхронности-при-запуске-alembic
 2: https://github.com/sqlalchemy/alembic/issues/805
 3: https://pressanybutton.ru/post/servis-na-fastapi/fastapi-4-model-polzovatelya-i-alembic/
 4: https://dev.to/matib/alembic-with-async-sqlalchemy-1ga
 5: https://habr.com/ru/companies/amvera/articles/849836/
 
Из кулинарной книги алембика (ссылка получена из дискуссии на гитхабе):
https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic