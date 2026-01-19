from src.repositories.bookings import BookingsRepository
from src.repositories.facilities import FacilitiesRepository
from src.repositories.hotels import HotelsRepository
from src.repositories.rooms import RoomsRepository
from src.repositories.users import UsersRepository

# Контекстный менеджер в Python — это объект, который определяет
# методы __enter__() и __exit__() и используется с инструкцией with.
# Вот пример использования контекстного менеджера для работы с файлом
#
# with open('file.txt', 'r') as file:
#     data = file.read()
#     # действия с данными
#
# # здесь файл уже закрыт
#
# В этом примере контекстный менеджер открывает файл и автоматически
# закрывает его после выполнения блока кода внутри with.
#
# Вы также можете создать свой собственный контекстный менеджер, определив
# класс с методами __enter__() и __exit__(). Вот пример создания контекстного
# менеджера для измерения времени выполнения кода:
#
# import time
#
# class Timer:
#     def __enter__(self):
#         self.start = time.time()
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.end = time.time()
#         print(f'Время выполнения: {self.end - self.start:.2f} секунд')
#
# with Timer():
#     # код, время выполнения которого нужно измерить
#     time.sleep(2)
#
# В этом примере метод __enter__() фиксирует время начала, а метод __exit__()
# вычисляет и выводит продолжительность выполнения кода внутри блока with.


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        # session_factory - фабрика сессий
        self.session = self.session_factory()

        self.hotels = HotelsRepository(self.session)
        self.rooms = RoomsRepository(self.session)
        self.users = UsersRepository(self.session)
        self.bookings = BookingsRepository(self.session)
        self.facilities = FacilitiesRepository(self.session)

        return self

    # async def __aexit__(self, exc_type, exc_val, exc_tb):
    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

