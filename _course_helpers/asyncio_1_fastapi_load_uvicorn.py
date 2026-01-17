import asyncio
import time
import threading

from fastapi import FastAPI
import uvicorn

app = FastAPI(docs_url=None)


@app.get("/sync/{id}")
def sync_func(id: int):
    print(f"sync. Потоков: {threading.active_count()}")
    time_start = time.time()
    print(f"sync. Начал {id}: {time_start:.2f}")
    # print(f"sync. Начал {id}: {time_start:.2f}")
    time.sleep(3)
    time_end = time.time()
    print(f"sync. Закончил {id}: {time_end:.2f}. Разница: {time_end-time_start}")
    # print(f"sync. Закончил {id}: {time.time():.2f}")


@app.get("/async/{id}")
async def async_func(id: int):
    print(f"async. Потоков: {threading.active_count()}")
    time_start = time.time()
    print(f"async. Начал {id}: {time_start:.2f}")
    # print(f"async. Начал {id}: {time.time():.2f}")
    await asyncio.sleep(3)
    # В операторе time_end = time.time() выдаёт ошибку:
    # ConnectionRefusedError: [WinError 1225] Удаленный компьютер отклонил это сетевое подключение
    # При запуске до 500 итераций (переменная range_num в «asyncio_01_2_fastapi_load_test_main.py»)
    # работает. Если запускать 1000, то ошибка.
    # Возможная ситуация (ответ в телеграм-чате https://t.me/c/2303072202/82/2288)
    # Скорее всего, что количество возможных одновременных запросов зависит от мощности
    # компьютера: https://stackoverflow.com/a/18585541
    # Решение (ответ в телеграм-чате https://t.me/c/2303072202/82/2290):
    # Самый лучший вариант — ставить ограничение на количество запросов в веб сервере.
    # В конце курса мы поставим nginx и я покажу, как можно ограничить количество
    # запросов в секунду от одного клиента, чтобы нас не смогли за dos’ить
    time_end = time.time()
    print(f"async. Закончил {id}: {time_end:.2f}. Разница: {time_end-time_start}")
    # print(f"async. Закончил {id}: {time.time():.2f}")


if __name__ == "__main__":
    uvicorn.run("asyncio_01_1_fastapi_load_test:app", reload=True)      # , port=8000




