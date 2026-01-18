from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, INT
from src.database import Base


class UsersORM(Base):
    # Наименование таблицы
    __tablename__ = "users"

    # Столбцы

    # Первичный ключ, уникальное значение
    id: Mapped[int] = mapped_column(primary_key=True)

    # Электронная почта пользователя
    email: Mapped[str] = mapped_column(String(length=200), unique=True)

    # Хэшированный пароль.
    hashed_password: Mapped[str] = mapped_column(String(length=200))

    # # Ниже строки не внесены в БД, потом обработать надо.
    # # Это гипотетические параметры о пользователе.
    # # Ник
    # nick_name: str | None = None
    #
    # # Полное имя
    # full_name: str | None = None
    #
    # # Заблокирован пользователь или нет
    # disabled: bool | None = None
    #
    # Дата создания пользователя
    # created_at
    #
    # Создание собственного API на Python (FastAPI): Router
    # и асинхронные запросы в PostgreSQL (SQLAlchemy)
    # https://habr.com/ru/articles/828328/
    # model_config = ConfigDict(from_attributes=True)
    #
    # Указывается она в начале описания модели и я советую вам ее
    # всегда указывать, когда речь идет про взаимодействие с базой
    # данных через алхимию. Тем самым Pydantic понимает явно, что
    # работать он будет с аргументами базы данных.
    # from datetime import datetime, date
    # from typing import Optional
    # import re
    # from pydantic import BaseModel, Field, EmailStr, validator
    # class SStudent(BaseModel):
    #     model_config = ConfigDict(from_attributes=True)
    #     id: int
    #     phone_number: str = Field(..., description="Номер телефона в международном формате, начинающийся с '+'")
    #     first_name: str = Field(..., min_length=1, max_length=50, description="Имя студента, от 1 до 50 символов")
    #     last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия студента, от 1 до 50 символов")
    #     date_of_birth: date = Field(..., description="Дата рождения студента в формате ГГГГ-ММ-ДД")
    #     email: EmailStr = Field(..., description="Электронная почта студента")
    #     address: str = Field(..., min_length=10, max_length=200, description="Адрес студента, не более 200 символов")
    #     enrollment_year: int = Field(..., ge=2002, description="Год поступления должен быть не меньше 2002")
    #     major_id: int = Field(..., ge=1, description="ID специальности студента")
    #     course: int = Field(..., ge=1, le=5, description="Курс должен быть в диапазоне от 1 до 5")
    #     special_notes: Optional[str] = Field(None, max_length=500, description="Дополнительные заметки, не более 500 символов")
    #
    #     @validator("phone_number")
    #     def validate_phone_number(cls, value):
    #         if not re.match(r'^\+\d{1,15}$', value):
    #             raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
    #         return value
    #
    #     @validator("date_of_birth")
    #     def validate_date_of_birth(cls, value):
    #         if value and value >= datetime.now().date():
    #             raise ValueError('Дата рождения должна быть в прошлом')
    #         return value



