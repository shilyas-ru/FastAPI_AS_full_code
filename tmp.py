""" Body - Множество параметров ->
        Несколько параметров тела запроса -> Python 3.10+
https://fastapi.tiangolo.com/ru/tutorial/body-multiple-params/?h=#_1
    В этом случае FastAPI заметит, что в функции есть более одного
параметра тела (два параметра, которые являются моделями Pydantic).
    Таким образом, имена параметров будут использоваться в качестве ключей
(имён полей) в теле запроса, и будет ожидаться запрос следующего формата:
...
"""

import uvicorn
from fastapi import FastAPI
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


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results

if __name__ == "__main__":
    uvicorn.run("tmp:app", host="127.0.0.1", port=8000, reload=True)

