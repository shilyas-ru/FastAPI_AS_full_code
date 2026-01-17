import uvicorn
from fastapi import FastAPI

# Следующая строка использует файл Routers_FastAPI/hotels_full_file.py
# В нём не используются схемы пи
# from Routers_FastAPI.hotels_full_file import router as router_hotels
# Следующая строка использует файл Routers_FastAPI/hotels_schemas.py
# from Routers_FastAPI.hotels_schemas import router as router_hotels
# Следующая строка использует файл Routers_FastAPI/hotels_schemas_examples.py
from Routers_FastAPI.hotels_schemas_examples import router as router_hotels

"""
## Задание №2: Пагинация для отелей. Часть 1

Необходимо реализовать пагинацию для отелей.

Для этого необходимо добавить 2 query параметра page и per_page,
оба параметра являются необязательными. Если пользователь не передает
page, то используется значение по умолчанию 1 (то есть первая страница).
Для per_page ситуация аналогичная — если параметр не передается,
то используется значение по умолчанию 3 (можете выбрать любое другое).
"""

"""
Импорт роутеров в справке.
    Учебник - Руководство пользователя -> Bigger Applications - Multiple Files
    https://fastapi.tiangolo.com/tutorial/bigger-applications/

An example file structure¶
Let's say you have a file structure like this:
.
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   └── routers
│   │   ├── __init__.py
│   │   ├── items.py
│   │   └── users.py
│   └── internal
│       ├── __init__.py
│       └── admin.py

    Раздел "Import the APIRouter"
    https://fastapi.tiangolo.com/ru/tutorial/bigger-applications/#import-the-apirouter
Файл: app/main.py

from fastapi import Depends, FastAPI

from .dependencies import get_query_token, get_token_header
from .internal import admin
from .routers import items, users

app = FastAPI(dependencies=[Depends(get_query_token)])


app.include_router(users.router)
app.include_router(items.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)

"""

tags_metadata = {
    "title": "Приложение по работе с отелями",
    "summary": "short summary of the API",
    "version": "ver. 0.2.0",  # По умолчанию version = "0.1.0", Source code in fastapi/applications.py
    "description": "Описание подробное."
                   "<br><br>Полезные ссылки:  "
                   "<ul>"
                   "<li>описание метатегов (metadata) "
                   '<a href="https://fastapi.qubitpi.org/reference/fastapi/#fastapi.FastAPI--example">'
                   "сторонний сайт</a> или "
                   '<a href="https://fastapi.tiangolo.com/reference/fastapi/#fastapi.FastAPI--example">'
                   "документация FastAPI</a>.</li>"
                   "<li>Metadata and Docs URLs -> Metadata for API "
                   '<a href="https://fastapi.qubitpi.org/tutorial/metadata/#metadata-for-api">'
                   "сторонний сайт</a> или "
                   '<a href="https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-api">'
                   "документация FastAPI</a>.</li>"
                   '<li><a href="https://habr.com/ru/companies/amvera/articles/851642/">'
                   "Pydantic 2: Полное руководство для Python-разработчиков - "
                   "от основ до продвинутых техник</a>.</li>"
                   "</ul>"
}

"""
URL-адреса метаданных и документации
https://fastapi.tiangolo.com/ru/tutorial/metadata/
"""

openapi_tags = [
    {
        "name": "Отели",
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
app.include_router(router_hotels)


if __name__ == "__main__":
    uvicorn.run("main:app",
                host="127.0.0.1",
                port=8000,
                reload=True)
