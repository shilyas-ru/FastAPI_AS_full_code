from datetime import datetime, timezone, timedelta

import jwt
from passlib.context import CryptContext

from src.config import settings


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Упрощённый вариант:
    # def create_access_token(data: dict) -> str:
    #     to_encode = data.copy()
    #     expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #     to_encode |= {"exp": expire}  # Синтаксис  |= появился с вер 3.9 и означает:
    #                                   # to_encode = to_encode | {"exp": expire}
    #                                   # Является аналогом to_encode.update({"exp": expire})
    #     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    #     return encoded_jwt

    # Вариант из документации
    # OAuth2 with Password (and hashing), Bearer with JWT tokens
    # https://fastapi.qubitpi.org/tutorial/security/oauth2-jwt/
    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()  # Копируем словарь, чтобы исходный словарь data не изменять
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode,
                                 settings.JWT_SECRET_KEY,
                                 algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    def hashed_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    # Вариант из документации
    # OAuth2 with Password (and hashing), Bearer with JWT tokens
    # https://fastapi.qubitpi.org/tutorial/security/oauth2-jwt/
    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)


