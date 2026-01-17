import uvicorn
from fastapi import FastAPI

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
# Path(__file__) - позволяет определить путь текущего файла
# str(Path(__file__).parent - взять его родителя (папка src)
# str(Path(__file__).parent.parent - взять родителя папки src (корневая папка проекта)
# Добавление папки проекта в пути - делаем ДО всех импортов из проекта

# Следующая строка использует файл src/api/routers/hotels.py
from src.api.routers.hotels import router as router_hotels
# from src.config import settings
#
# print(f"{settings.DB_URL = }")

"""
## Задание №3: Миграция для номеров

Необходимо создать миграцию (в Alembic они называются ревизии/revisions) 
через терминал ровно так же, как мы делали это в уроке.
Внутри миграции должны появиться изменения: добавление новой таблицы rooms.
После создания миграцию необходимо прогнать (запустить/применить), чтобы 
в базе данных появилась таблица rooms
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
                   '<li><a href="https://habr.com/ru/articles/866536/">'
                   "Делаем управление конфигами удобным при помощи pydantic_settings</a>.</li>"
                   '<li><a href="https://habr.com/ru/companies/amvera/articles/855740/">'
                   "Асинхронный SQLAlchemy 2: улучшение кода, методы обновления и удаления данных</a>.</li>"
                   '<li><a href="https://stackoverflow.com/questions/73248731/alembic-store-extra-information-in-alembic-version-table">'
                   "Alembic — хранит дополнительную информацию в таблице `alembic_version` "
                   "(Alembic — store extra information in `alembic_version` table)</a>.</li>"
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
