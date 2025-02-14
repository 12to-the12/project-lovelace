import asyncio
from time import sleep


async def printerbrr():
    await asyncio.sleep(3)
    print("hi")


async def halloo():
    for _ in range(10):
        print("this is another task")
        await asyncio.sleep(0.1)
        print("and yet another")


async def main():
    a = asyncio.create_task(printerbrr())
    b = asyncio.create_task(halloo())
    await asyncio.gather(a, b)


asyncio.run(main())
