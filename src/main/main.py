import promptify


async def main() -> None:
    await promptify.run()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
