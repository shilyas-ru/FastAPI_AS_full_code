import uvicorn
from fastapi import FastAPI

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
# Path(__file__) - позволяет определить путь текущего файла
# str(Path(__file__).parent - взять его родителя (папка src)
# str(Path(__file__).parent.parent - взять родителя папки src (корневая папка проекта)
# Добавление папки проекта в пути - делаем ДО всех импортов из проекта

# Следующая строка использует файл src/api/routers/auth.py
from src.api.routers.auth import router as router_auth
from src.api.routers.rooms import router as router_rooms
from src.api.routers.hotels import router as router_hotels
from src.api.routers.bookings import router as router_bookings
from src.api.routers.facilities import router as router_facilities


"""
## Задание № 17: Получение удобств конкретного номера

Необходимо получать удобства в ручке для получения конкретного номера.

Для этого необходимо создать новый метод в репозитории RoomsRepository, 
который подгрузит удобства через relationship, и вызвать этот метод внутри ручки.
"""

tags_metadata = {
    "title": "Приложение по работе с отелями",
    "summary": "Задание № 17: Получение удобств конкретного номера",  # short summary of the API
    "version": "ver. 0.17.0",  # По умолчанию version = "0.1.0", Source code in fastapi/applications.py
    "description": "Тут должно быть подробное описание, но я размещу интересные для меня ссылки."
                   "<br><br>Полезные ссылки:  "
                   "<ul>"
                   "<li>документация FastAPI - FastAPI_documentation "
                   '<a href="https://github.com/amoglock/FastAPI_documentation/tree/master" '
                   'target="_blank">альтернативный русский перевод</a>.</li>'
                   "<li>описание метатегов (metadata) "
                   '<a href="https://fastapi.qubitpi.org/reference/fastapi/#fastapi.FastAPI--example" '
                   'target="_blank">сторонний сайт</a> или '
                   '<a href="https://fastapi.tiangolo.com/reference/fastapi/#fastapi.FastAPI--example" '
                   'target="_blank">документация FastAPI</a>.</li>'
                   "<li>Metadata and Docs URLs -> Metadata for API "
                   '<a href="https://fastapi.qubitpi.org/tutorial/metadata/#metadata-for-api" '
                   'target="_blank">сторонний сайт</a> или '
                   '<a href="https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-api" '
                   'target="_blank">документация FastAPI</a>.</li>'
                   '<li><a href="https://habr.com/ru/companies/amvera/articles/851642/" '
                   'target="_blank">Pydantic 2: Полное руководство для '
                   "Python-разработчиков - от основ до продвинутых техник</a>.</li>"
                   '<li><a href="https://habr.com/ru/articles/866536/" target="_blank">'
                   "Делаем управление конфигами удобным при помощи pydantic_settings</a>.</li>"
                   '<li><a href="https://habr.com/ru/companies/amvera/articles/855740/" '
                   'target="_blank">Асинхронный SQLAlchemy 2: '
                   "улучшение кода, методы обновления и удаления данных</a>.</li>"
                   '<li><a href="https://habr.com/ru/companies/amvera/articles/863130/" '
                   'target="_blank">Создание блога на FastAPI с нуля: '
                   "JWT, Markdown и современный веб-дизайн</a>.</li>"
                   '<li><a href="https://stackoverflow.com/questions/73248731/'
                   'alembic-store-extra-information-in-alembic-version-table" target="_blank">'
                   "Alembic — хранит дополнительную информацию в таблице `alembic_version` "
                   "(Alembic — store extra information in `alembic_version` table)</a>.</li>"
                   '<li><a href="https://habr.com/ru/articles/735606/" target="_blank">'
                   "Что нового в SQLAlchemy 2.0?</a>.</li>"
                   '<li><a href="https://www.iditect.com/program-example/'
                   'how-to-update-sqlalchemy-orm-object-by-a-python-dict.html/" '
                   'target="_blank">'
                   "How to update sqlalchemy orm object by a python dict</a>.</li>"
                   '<li><a href="https://www.iditect.com/faq/python/'
                   'how-to-get-a-raw-compiled-sql-query-from-a-sqlalchemy-expression.html/" '
                   'target="_blank">'
                   "How to get a raw, compiled SQL query from a SQLAlchemy expression</a>.</li>"
                   '<li><a href="https://markdownlivepreview.com/" target="_blank">'
                   "Редактор markdown онлайн</a>.</li>"
                   '<li><a href="https://jwt.io/" target="_blank">'
                   "Проверка JWT токенов онлайн - jwt.io</a>.</li>"
                   '<li><a href="https://restfulapi.net/resource-naming/" target="_blank">'
                   "REST API URI Naming Conventions and Best Practices</a>.</li>"
                   '<li><a href="https://github.com/arthurio/fastapi-filter/blob/main/docs/index.md" '
                   'target="_blank">'
                   "FastAPI Filter</a>.</li>"
                   '<li><a href="https://habr.com/ru/articles/714570/" target="_blank">'
                   "Фильтрация и пагинация в FastAPI</a>.</li>"
                   "</ul>"
                   'В методе API `delete("/hotels")` можно получить список удаляемых записей '
                   "через параметр "
                   '<a href="https://docs.sqlalchemy.org/en/20/glossary.html'
                   '#term-RETURNING" target="_blank">'
                   'RETURNING (описание в Glossary)</a>. Этот же параметр используется в '
                   "репозитории в классе BaseRepository."
                   "<br>См. пояснение в документации: "
                   '<a href="https://docs.sqlalchemy.org/en/20/changelog/migration_06.html'
                   '#returning-support" target="_blank">'
                   "RETURNING Support</a>:<br>"
                   "The insert(), update() and delete() constructs now support a returning() method, "
                   "which corresponds to the SQL RETURNING clause as supported by PostgreSQL, Oracle, "
                   "MS-SQL, and Firebird. It is not supported for any other backend at this time.<br>"
                   "Given a list of column expressions in the same manner as that of a select() "
                   "construct, the values of these columns will be returned as a regular result set...<br><br>"
                   "Порядок вывода разделов задаётся в переменной openapi_tags в файле main.py - d каком "
                   "порядке указаны в openapi_tags записи - в таком они в документации "
                   "http://127.0.0.1:8000/docs и выводятся."
}

"""
URL-адреса метаданных и документации
https://fastapi.tiangolo.com/ru/tutorial/metadata/
"""


# В каком порядке указаны в openapi_tags записи - в таком они в документации и выводятся.
openapi_tags = [
    {
        "name": router_facilities.tags[0],
        "description": "Операции с удобствами в номерах.",
        "externalDocs":
            {
                "description": "Подробнее во внешней документации (www.example.com)",
                "url": "https://www.example.com/",
            }
    },
    {
        "name": router_bookings.tags[0],
        "description": "Операции с бронированием номеров.",
        "externalDocs":
            {
                "description": "Подробнее во внешней документации (www.example.com)",
                "url": "https://www.example.com/",
            }
    },
    {
        "name": router_rooms.tags[0],
        "description": "Операции с номерами.",
        "externalDocs":
            {
                "description": "Подробнее во внешней документации (www.example.com)",
                "url": "https://www.example.com/",
            }
    },
    {
        "name": router_auth.tags[0],
        "description": "Операции с пользователями.",
        "externalDocs":
            {
                "description": "Подробнее во внешней документации (www.example.com)",
                "url": "https://www.example.com/",
            }
    },
    {
        "name": router_hotels.tags[0],
        "description": "Операции с отелями.",
        "externalDocs":
            {
                "description": "Подробнее во внешней документации (www.example.com)",
                "url": "https://www.example.com/",
            }
    },
]

app = FastAPI(**tags_metadata,
              openapi_tags=openapi_tags)

app.include_router(router_auth)
app.include_router(router_rooms)
app.include_router(router_hotels)
app.include_router(router_bookings)
app.include_router(router_facilities)


if __name__ == "__main__":
    uvicorn.run("main:app",
                host="127.0.0.1",
                port=8000,
                reload=True)
