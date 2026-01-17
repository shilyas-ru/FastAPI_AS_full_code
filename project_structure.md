## Структура проекта

```
.env: текстовый файл, который содержит переменные окружения
.env-example: текстовый файл, который содержит переменные 
              окружения с примером заполнения
.gitignore
alembic.ini
project_structure.md
requirements.txt
src
├── config.py
├── database.py
├── main.py
├── api: файлы приложения
│   ├── dependencies
│   │   ├── dependencies.py
│   ├── routers
│   │   ├── hotels.py
├── migration: файлы для миграций
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   ├── versions: файлы со сгенерированным кодом для миграций
│   │   ├── 6b2543281e38_001_create_table_hotels.py
│   │   ├── 426fb4662d04_002_create_rooms_hotels.py
├── models: файлы с моделями для работы с базой данных
│   ├── hotels.py
│   ├── rooms.py
├── schemas: файлы со схемами данных
│   ├── hotels.py
```