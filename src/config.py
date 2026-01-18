from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str

    @property
    def DB_URL(self):
        # Справка про подключение:
        # https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.asyncpg
        # Строка подключения (из справки):
        # postgresql+asyncpg://user:password@host:port/dbname[?key=value&key=value...]

        # postgresql://user:password@host:port/database_name
        # postgresql+asyncpg - это подключение к postgresql через драйвер (движок) asyncpg

        # settings.DB_URL = 'postgresql+asyncpg://postgres:postgres@localhost:5432/booking'
        # return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # model_config = SettingsConfigDict(env_file=".env")
    # Комментарий к уроку: В отличие от видео, у меня в конструкции
    # model_config = SettingsConfigDict(env_file="...") виден текущий каталог, то есть src.
    # урок: https://artemshumeiko.zenclass.ru/student/courses/937c3a35-998d-4420-bd3d-9f64db23be23/lessons/173b9d0b-0fb4-42a7-8a9a-6cd3baaec62b
    # Можно в настройках Run -> Edit Configurations поменять рабочую директорию (Working directory:) на папку проекта.

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str  # Алгоритм по умолчанию
    ACCESS_TOKEN_EXPIRE_MINUTES: int  # Количество минут, сколько токен будет жить

    model_config = SettingsConfigDict(env_file=f"{Path(__file__).parent.parent / '.env'}")


settings = Settings()
