import asyncio

from src.services import run_parser_wb


async def main():
    await run_parser_wb()


if __name__ == '__main__':
    asyncio.run(main())
