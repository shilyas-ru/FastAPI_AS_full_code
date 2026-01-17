import asyncio
# Установка: pip install aiohttp
# https://docs.aiohttp.org/en/stable/index.html
# https://pypi.org/project/aiohttp/
import aiohttp

import uvicorn


async def get_data(id: int, endpoint: str):
    print(f"Начал выполнение: {id}")
    url = f"http://127.0.0.1:8000/{endpoint}/{id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print(f"Закончил выполнение: {id}")


async def main(range_num=3, func_type="async"):
    # await asyncio.gather(*get_data(i, "async") for i in range(3))
    await asyncio.gather(*[get_data(i, func_type) for i in range(range_num)])


if __name__ == "__main__":
    range_num = 1000

    func_type = "async"
    print(f"Метод {func_type}")
    asyncio.run(main(range_num=range_num, func_type=func_type))

    # func_type = "sync"
    # print(f"\n\nМетод {func_type}")
    # asyncio.run(main(range_num=range_num, func_type=func_type))
