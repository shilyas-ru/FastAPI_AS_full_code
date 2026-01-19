from pydantic import BaseModel, Field, ConfigDict

from src.schemas.facilities import FacilityPydanticSchema

# Pydantic 2: Полное руководство для Python-разработчиков — от основ до продвинутых техник
# https://fastapi.qubitpi.org/reference/fastapi/?h=tags_metadata#fastapi.FastAPI--example

# См. документацию про примеры:
# https://fastapi.tiangolo.com/ru/tutorial/schema-extra-example/?h=#body-with-multiple-examples
# https://fastapi.qubitpi.org/tutorial/schema-extra-example/?h=#body-with-multiple-examples


room_descr = {"hotel_id": "Идентификатор отеля, в котором находится комната",
              "title": "Название номера",
              "description": "Описание номера",
              "price": "Цена номера",
              "quantity": "Общее количество номеров такого типа",
              "facilities_ids": "Список из идентификаторов удобств",
              }

room_examples = {"hotel_id": 214,  # int, Идентификатор отеля, в котором находится комната
                 "title": "Название номера",  # String(length=100)
                 "description": "Описание номера",  # str
                 "price": 2,  # int, Цена номера
                 "quantity": 3,  # int, Общее количество номеров такого типа
                 "facilities_ids": []  # list[int] | [], Список из идентификаторов удобств
                 }

"""
Можно было бы описать один класс так:
class HotelDescription(BaseModel):
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
                hotel_caption: Annotated[HotelDescription, Body()] = HotelDescription(hotel_title=None,
                                                                              hotel_name=None),
                ):

Но этот метод плох тем, что через метод Body() можно передать с json значение None 
и pydantic его пропустит, например, так:
{
  "hotel_title": null,
  "hotel_name": "string"
}
"""


class HotelPath(BaseModel):
    # Поля указываем такие же, как в дальнейшем будем указывать в ссылках:
    # @router.delete("/{hotel_id}",...
    # Если поле в классе и имя переменной в ссылке будут различными, то возникнет
    # ошибка "422 unprocessable entity"
    hotel_id: int = Field(description="Идентификатор отеля",
                          ge=1,
                          examples=[1],
                          )


class RoomPath(BaseModel):
    # Поля указываем такие же, как в дальнейшем будем указывать в ссылках:
    # @router.delete("/{hotel_id}",...
    # Если поле в классе и имя переменной в ссылке будут различными, то возникнет
    # ошибка "422 unprocessable entity"
    room_id: int = Field(description="Идентификатор комнаты",
                         ge=1,
                         examples=[1],
                         )


class HotelRoomPath(RoomPath, HotelPath):
    pass


class RoomDescrRecRequest(BaseModel):
    # Поля указываем такие же, как именованы колонки в таблице
    # rooms (класс RoomsORM в файле src\models\rooms.py).
    title: str = Field(description=room_descr["title"],
                       min_length=3,
                       examples=[room_examples["title"]],
                       )
    description: str = Field(description=room_descr["description"],
                             min_length=10,
                             # max_length=50,
                             examples=[room_examples["description"]],
                             )
    price: int = Field(ge=1,
                       examples=[room_examples["price"]],
                       )
    quantity: int = Field(ge=1,
                          examples=[room_examples["quantity"]],
                          )
    # Список из идентификаторов удобств
    facilities_ids: list[int] = Field(examples=[room_examples["facilities_ids"]])
    # facilities_ids: list[int] = []


class RoomDescriptionRecURL(RoomDescrRecRequest):
    # Поля указываем такие же, как именованы колонки в таблице
    # rooms (класс RoomsORM в файле src\models\rooms.py).
    hotel_id: int = Field(description=room_descr["title"],
                          ge=1,
                          examples=[room_examples["hotel_id"]],
                          )
    # title: str = Field(description=room_descr["title"],
    #                    min_length=3,
    #                    examples=[room_examples["title"]],
    #                    )
    # description: str = Field(description=room_descr["description"],
    #                          min_length=10,
    #                          # max_length=50,
    #                          examples=[room_examples["description"]],
    #                          )
    # price: int = Field(ge=1,
    #                    examples=[room_examples["price"]],
    #                    )
    # quantity: int = Field(ge=1,
    #                       examples=[room_examples["quantity"]],
    #                       )


class RoomDescrOptRequest(BaseModel):
    # Поля указываем такие же, как именованы колонки в таблице
    # rooms (класс RoomsORM в файле src\models\rooms.py).
    #
    # Этот класс используется, когда надо обновить КАКИЕ-то поля,
    # а не все поля сразу. Поэтому для полей устанавливается
    # возможность при определении типа поля, например: str | None
    # и указывается значение по умолчанию: default=None
    title: str | None = Field(default=None,
                              description=room_descr["title"],
                              min_length=3,
                              examples=[room_examples["title"]],
                              )
    description: str | None = Field(default=None,
                                    description=room_descr["description"],
                                    min_length=10,
                                    # max_length=50,
                                    examples=[room_examples["description"]],
                                    )
    price: int | None = Field(default=None,
                              ge=1,
                              examples=[room_examples["price"]],
                              )
    quantity: int | None = Field(default=None,
                                 ge=1,
                                 examples=[room_examples["quantity"]],
                                 )
    # Список из идентификаторов удобств
    # facilities_ids: list[int] = []
    facilities_ids: list[int] = Field(default=[],
                                      examples=[room_examples["facilities_ids"]]
                                      )


class RoomDescriptionOptURL(RoomDescrOptRequest):
    # Поля указываем такие же, как именованы колонки в таблице
    # rooms (класс RoomsORM в файле src\models\rooms.py).
    #
    # Этот класс используется, когда надо обновить КАКИЕ-то поля,
    # а не все поля сразу. Поэтому для полей устанавливается
    # возможность при определении типа поля, например: str | None
    # и указывается значение по умолчанию: default=None
    hotel_id: int | None = Field(default=None,
                                 description=room_descr["title"],
                                 ge=1,
                                 examples=[room_examples["hotel_id"]],
                                 )
    # title: str | None = Field(default=None,
    #                           description=room_descr["title"],
    #                           min_length=3,
    #                           examples=[room_examples["title"]],
    #                           )
    # description: str | None = Field(default=None,
    #                                 description=room_descr["description"],
    #                                 min_length=10,
    #                                 # max_length=50,
    #                                 examples=[room_examples["description"]],
    #                                 )
    # price: int | None = Field(default=None,
    #                           ge=1,
    #                           examples=[room_examples["price"]],
    #                           )
    # quantity: int | None = Field(default=None,
    #                              ge=1,
    #                              examples=[room_examples["quantity"]],
    #                              )


class RoomBase(BaseModel):
    # Поля указываем такие же, как именованы колонки в таблице
    # rooms (класс RoomsORM в файле src\models\rooms.py).
    # Если не указать значение None, как возможный вариант, то при
    # конвертации в эту схему некоторой модели, имеющей пустые поля,
    # будет ошибка (в поле description ничего нет, т.е., значение None):
    # pydantic_core._pydantic_core.ValidationError: 1 validation error for RoomPydanticSchema
    # description
    #   Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    #     For further information visit https://errors.pydantic.dev/2.10/v/string_type
    hotel_id: int | None
    title: str | None
    description: str | None
    price: int | None
    quantity: int | None


class RoomPydanticSchema(RoomBase):
    # Эта схема должна иметь такие же поля, как указаны в схеме
    # для отелей - rooms (класс RoomsORM в файле src\models\rooms.py).
    # Поле title и прочие поля наследуем от родителя.
    id: int

    model_config = ConfigDict(from_attributes=True)

# async def change_room_hotel_id_put(hotelroom: Annotated[HotelRoomPath, Path()],
#                                    room_params: Annotated[RoomDescrRecRequest,
#                                                           Body()],
#                                    db: DBDep,
#                                    ):
#     _room_params = RoomDescriptionRecURL(hotel_id=hotelroom.hotel_id,
#                                          **room_params.model_dump())


class RoomWithRels(RoomPydanticSchema):
    # FacilityPydanticSchema - схема с title и id.
    # Предполагаем, что какое-то значение всегда будет - пустой массив или
    # массив с данными, но будет. Поэтому значение по умолчанию не делаем.
    facilities: list[FacilityPydanticSchema]
