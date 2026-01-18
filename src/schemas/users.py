from pydantic import BaseModel, ConfigDict, EmailStr
# Для работы с полем EmailStr требуется установить:
# pip install pydantic[email]
# Installing collected packages: dnspython, email-validator


class UserDescriptionRecURL(BaseModel):
    email: EmailStr
    password: str


class UserBase(BaseModel):
    email: EmailStr
    hashed_password: str


class UserPydanticSchema(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)