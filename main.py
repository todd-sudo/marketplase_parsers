import asyncio
import time

from src.willdberies import gather_data, get_products_id


def main():
    start_time = time.monotonic()
    asyncio.run(gather_data())
    print(f"Потрачено времени: {(time.monotonic() - start_time) / 60} минут")


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    main()
