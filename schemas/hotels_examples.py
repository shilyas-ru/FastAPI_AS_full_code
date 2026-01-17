from pydantic import BaseModel, Field


# Pydantic 2: Полное руководство для Python-разработчиков — от основ до продвинутых техник
# https://fastapi.qubitpi.org/reference/fastapi/?h=tags_metadata#fastapi.FastAPI--example


class HotelPath(BaseModel):
    hotel_id: int = Field(description="Идентификатор отеля",
                          ge=1,
                          )


# Модели pydantic, заканчивающиеся на Test - используются только в тестовоё ручке
# @router.post("/test/{hotel_id}/{room_id}",
#              summary="Тестовая ручка для демо методов Path(), "
#                      "Query(), Body() со схемами Pydantic",
#              tags=["Отели"])
# def hotel_test_post(room_path: Annotated[RoomPathTest, Path()],
#                     hotel_query_data: Annotated[HotelQueryTest, Query()],
#                     hotel_body_data: Annotated[HotelBodyTest, Body()],
#                     ):
#     return f"{room_path.hotel_id = }, {room_path.room_id = }, " \
#            f"{room_path = }, {hotel_query_data = }, {hotel_body_data = }"


class RoomPathTest(HotelPath):
    room_id: int = Field(description="Идентификатор комнаты",
                         ge=1,
                         )
    room_number: int = Field(description="Номер комнаты (от 1 до 5)",
                             ge=1,
                             le=5,
                             )


class HotelQueryTest(BaseModel):
    hotel_title: str = Field(description="Название (title) отеля",
                             min_length=3,
                             )
    hotel_name: str = Field(default="name",
                            description="Название (name) отеля",
                            max_length=50,
                            )


class HotelBodyTest(BaseModel):
    hotel_body_str: str = Field(default="name",
                                description="Данные hotel body str (title)",
                                min_length=3,
                                )
    hotel_body_int: int = Field(default=1,
                                description="Данные hotel body int",
                                ge=1,
                                )
    # См. документацию про примеры:
    # https://fastapi.tiangolo.com/ru/tutorial/schema-extra-example/?h=#body-with-multiple-examples
    # https://fastapi.qubitpi.org/tutorial/schema-extra-example/?h=#body-with-multiple-examples
    model_config = {
        "json_schema_extra": {
            # порядок вывод полей - алфавитный, а не как указано в коде.
            "examples": [
                {
                    "hotel_body_str": "data for hotel_body_str",
                    "hotel_body_int": 33,
                }
            ]
        }
    }


class ItemTest(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


hotel = {"title": "Название (title) отеля",
         "name": "Название (name) отеля",
         }

"""
Можно было бы описать один класс так:
class HotelCaption(BaseModel):
    hotel_title: str | None = Field(description=hotel["title"],
                                    min_length=3,
                                    )
    hotel_name: str | None = Field(description=hotel["name"],
                                   max_length=50,
                                   )
В этом случае параметры не имеют значения, присвоенного по умолчанию,
и должны считаться обязательными.
Чтобы сделать присвоение значений по умолчанию, можно в описании ручки сделать так:
@router.patch("/{hotel_id}",
              tags=["Отели"],
              summary="Обновление каких-либо данных выборочно или всех данных сразу",
              )
def hotel_patch(hotel_path: Annotated[HotelPath, Path()],
                hotel_caption: Annotated[HotelCaption, Body()] = HotelCaption(hotel_title=None,
                                                                              hotel_name=None),
                ):

Но этот метод плох тем, что через метод Body() можно передать с json значение None 
и pydantic его пропустит, например, так:
{
  "hotel_title": null,
  "hotel_name": "string"
}
"""


class HotelCaptionRec(BaseModel):
    hotel_title: str = Field(description=hotel["title"],
                             min_length=3,
                             )
    hotel_name: str = Field(description=hotel["name"],
                            max_length=50,
                            )


class HotelCaptionOpt(BaseModel):
    hotel_title: str | None = Field(default=None,
                                    description=hotel["title"],
                                    min_length=3,
                                    )
    hotel_name: str | None = Field(default=None,
                                   description=hotel["name"],
                                   max_length=50,
                                   )
