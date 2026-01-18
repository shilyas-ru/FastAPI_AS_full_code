from datetime import datetime, timezone, timedelta

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

from src.config import settings


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # кодирования/декодирования JWT-токенов.
    def decrypt_token(self, coded_token: str) -> str:
        # Расшифровать токен Сделано для того, чтобы токен
        # нельзя было расшифровать штатными инструментами.
        # По факту удаляется ранее добавленный в токен "мусор",
        # препятствующий использованию штатных "расшифровщиков".
        coded_token_token_lst = coded_token.split('.')
        decode_token = (coded_token_token_lst[0][:-1] + '.' +
                        coded_token_token_lst[1][:-1] + '.' +
                        coded_token_token_lst[2][:-1])
        return decode_token

    def encrypt_token(self, token: str) -> str:
        # Зашифровать токен. Сделано для того, чтобы токен
        # нельзя было расшифровать штатными инструментами.
        # По факту в токен добавляется некоторый "мусор",
        # препятствующий использованию штатных "расшифровщиков".
        token_lst = token.split('.')
        coded_token = (token_lst[0] + '1.' +
                       token_lst[1] + '2.' +
                       token_lst[2] + '3')
        return coded_token

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
    # def create_access_token(self, data: dict,
    #                         expires_delta: timedelta | None = None) -> str:
    def create_access_token(self, data: dict,
                            validity_period: dict | None = None) -> str:
        to_encode = data.copy()  # Копируем словарь, чтобы исходный словарь data не изменять
        if validity_period is None:
            validity_period = {"minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES}
        expires_delta = timedelta(**validity_period)
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode,
                                 settings.JWT_SECRET_KEY,
                                 algorithm=settings.JWT_ALGORITHM)
        encoded_jwt = self.encrypt_token(encoded_jwt)
        return encoded_jwt

    def hashed_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    # Вариант из документации
    # OAuth2 with Password (and hashing), Bearer with JWT tokens
    # https://fastapi.qubitpi.org/tutorial/security/oauth2-jwt/
    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    # def decode_token(self, token: str) -> dict:  # dict(str, Any)
    #     return jwt.decode(token,
    #                       settings.JWT_SECRET_KEY,
    #                       algorithms=[settings.JWT_ALGORITHM])
    def decode_token(self, token: str) -> dict:  # dict(str, Any)
        decode_token = self.decrypt_token(token)
        try:
            return jwt.decode(decode_token,
                              settings.JWT_SECRET_KEY,
                              algorithms=[settings.JWT_ALGORITHM])
        except jwt.exceptions.InvalidSignatureError:
            # Пользователь не авторизовался
            # status_code=401: не аутентифицирован
            raise HTTPException(status_code=401,
                                detail="Не верный токен")
        except jwt.exceptions.ExpiredSignatureError:
            # Пользователь не авторизовался
            # status_code=401: не аутентифицирован
            raise HTTPException(status_code=401,
                                detail="Истек срок действия подписи. Перелогиньтесь")

