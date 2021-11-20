import asyncio
import time

from .willdberies import gather_data
from src.core.settings import start, finish


def run_parser_wb():
    start_time = time.monotonic()
    asyncio.run(gather_data(start, finish))
    print(f"Потрачено времени: {(time.monotonic() - start_time) / 60} минут")
