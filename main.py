import asyncio
import time

from src.willdberies import get_products_id


def main():
    start_time = time.monotonic()
    asyncio.run(get_products_id())
    print(f"Потрачено времени: {(time.monotonic() - start_time) / 60} минут")


if __name__ == '__main__':
    main()
