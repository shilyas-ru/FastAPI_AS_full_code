from typing import Annotated, get_type_hints
import sys

x: Annotated[int, 'Метаданные', 'Еще метаданные'] = 10

print(get_type_hints(sys.modules[__name__]))
print(get_type_hints(sys.modules[__name__], include_extras=True))
print(get_type_hints(sys.modules[__name__], include_extras=True)['x'].__metadata__)
print(get_type_hints(sys.modules[__name__], include_extras=True)['x'].__metadata__[0])
print(get_type_hints(sys.modules[__name__], include_extras=True)['x'].__metadata__[1])

tags_metadata = {
    "title": "ChimichangApp",
    "summary": "short summary of the API",
    "description": "Описание подробное."
                   "\n\n"
                   "[Pydantic 2: Полное руководство для Python-разработчиков — от основ до продвинутых техник]"
                   "(https://habr.com/ru/companies/amvera/articles/851642/)",
    }