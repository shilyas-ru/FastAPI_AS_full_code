""" Body - Множество параметров -> Отдельные значения в теле запроса ->
        Other versions and variants -> Python 3.10+ - non-Annotated
https://fastapi.tiangolo.com/ru/tutorial/body-multiple-params/?h=#_2
    Например, расширяя предыдущую модель, вы можете решить, что вам нужен
еще один ключ importance в том же теле запроса, помимо параметров item и user.
    Если вы объявите его без указания, какой именно объект (Path,
Query, Body и .т.п.) ожидаете, то, поскольку это является простым
типом данных, FastAPI будет считать, что это query-параметр.
...
"""
import uvicorn
from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class User(BaseModel):
    username: str
    full_name: str | None = None


@app.put("/items_None/{item_id}")
async def update_item1_1(item_id: int,
                         item: Item, user: User,
                         importance: int = Body()):  # по умолчанию embed=None
    """
    Функция принимает два словаря и целое значение в теле запроса, параметр передаётся в URL.

    В теле запроса данные передаются:
    - item: Item, тип данных: class Item(BaseModel)
    - user: User, тип данных: class User(BaseModel)
    - importance: int = Body(), по умолчанию embed=None
    """
    # В этом случае передаются данные (Request body) в виде словаря:
    # {
    #   "item": {
    #     "name": "string",
    #     "description": "string",
    #     "price": 0,
    #     "tax": 0
    #   },
    #   "user": {
    #     "username": "string",
    #     "full_name": "string"
    #   },
    #   "importance": 0
    # }
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results


@app.put("/items_False/{item_id}")
async def update_item1_2(item_id: int,
                         item: Item, user: User,
                         importance: int = Body(embed=False)):
    """
    Функция принимает два словаря и целое значение в теле запроса, параметр передаётся в URL.

    В теле запроса данные передаются:
    - item: Item, тип данных: class Item(BaseModel)
    - user: User, тип данных: class User(BaseModel)
    - importance: int = Body(embed=False)
    """
    # В этом случае передаются данные (Request body) в виде словаря:
    # {
    #   "item": {
    #     "name": "string",
    #     "description": "string",
    #     "price": 0,
    #     "tax": 0
    #   },
    #   "user": {
    #     "username": "string",
    #     "full_name": "string"
    #   },
    #   "importance": 0
    # }
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results


@app.put("/items_True/{item_id}")
async def update_item1_3(item_id: int,
                         item: Item, user: User,
                         importance: int = Body(embed=True)):
    """
    Функция принимает два словаря и целое значение в теле запроса, параметр передаётся в URL.

    В теле запроса данные передаются:
    - item: Item, тип данных: class Item(BaseModel)
    - user: User, тип данных: class User(BaseModel)
    - importance: int = Body(embed=True)
    """
    # В этом случае передаются данные (Request body) в виде словаря:
    # {
    #   "item": {
    #     "name": "string",
    #     "description": "string",
    #     "price": 0,
    #     "tax": 0
    #   },
    #   "user": {
    #     "username": "string",
    #     "full_name": "string"
    #   },
    #   "importance": 0
    # }
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results


@app.put("/item_embed_True/{item_id}")
async def update_item2_1(item_id: int, importance: int = Body(embed=True)):
    """
    Функция принимает целое значение в теле запроса, параметр передаётся в URL.

    В теле запроса данные передаются: importance: int = Body(embed=True)
    """
    # В этом случае передаются данные (Request body) в виде словаря:
    #   {
    #     "importance": 0
    #   }
    results = {"item_id": item_id, "importance": importance}
    return results


@app.put("/item_embed_False/{item_id}")
async def update_item2_2(item_id: int, importance: int = Body(embed=False)):
    """
    Функция принимает целое значение в теле запроса, параметр передаётся в URL.

    В теле запроса данные передаются: importance: int = Body(embed=False)
    """
    # В этом случае передаются данные (Request body) в виде значения:
    #   0
    results = {"item_id": item_id, "importance": importance}
    return results


@app.put("/item_embed_None/{item_id}")
async def update_item2_3(item_id: int, importance: int = Body()):  # по умолчанию embed=None
    """
    Функция принимает целое значение в теле запроса, параметр передаётся в URL.

    В теле запроса данные передаются: importance: int = Body(), по умолчанию embed=None
    """
    # В этом случае передаются данные (Request body) в виде значения:
    #   0
    results = {"item_id": item_id, "importance": importance}
    return results


if __name__ == "__main__":
    uvicorn.run("temp:app", host="127.0.0.1", port=8000, reload=True)

