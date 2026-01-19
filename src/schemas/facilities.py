from pydantic import BaseModel, Field, ConfigDict


hotel = {"title": "Название отеля",
         "location": "Местонахождение (адрес) отеля",
         }

hotel_examples = {"title": "Название отеля",
                  "location": "Местонахождение (адрес) отеля",
                  }


class FacilityDescriptionRecURL(BaseModel):
    # Поля указываем такие же, как именованы колонки в таблице
    # hotels (класс HotelsORM в файле src\models\hotels.py).
    title: str = Field(description=hotel["title"],
                       min_length=3,
                       examples=[hotel_examples["title"]],
                       )


class FacilityBase(BaseModel):
    # Поля указываем такие же, как именованы колонки в таблице
    # facilities (класс FacilitiesORM в файле src\models\facilities.py).
    title: str | None = Field(default=None)


class FacilityPydanticSchema(FacilityBase):
    # Эта схема должна иметь такие же поля, как указаны в схеме
    # для удобств - facilities (класс FacilitiesORM в файле src\models\facilities.py).
    # Поле title наследуем от родителя.
    id: int = Field()

    model_config = ConfigDict(from_attributes=True)
