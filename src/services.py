import asyncio
import time

from .willdberies import gather_data


def run_parser_wb():
    start_time = time.monotonic()
    asyncio.run(gather_data())
    print(f"Потрачено времени: {(time.monotonic() - start_time) / 60} минут")
