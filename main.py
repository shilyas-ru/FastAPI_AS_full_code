import uvicorn
from fastapi import FastAPI

# Следующая строка использует файл Routers_FastAPI/hotels.py
from Routers_FastAPI.hotels import router as router_hotels

"""
## Дополнение к заданию №2: Пагинация для отелей

Сама пагинация делается через зависимости - Dependencies
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
