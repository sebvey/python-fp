import random

from xfp.a.functions import AFunc
import asyncio


async def random_wait(displayed: str):
    await asyncio.sleep(random.randint(1, 10))
    print(displayed)
    return displayed


async def times_two(s: str) -> str:
    await asyncio.sleep(random.randint(1, 10))
    print(f"{s}{s}")
    return f"{s}{s}"


ll = [AFunc(random_wait).async_map(times_two)(i) for i in ["bonjour", "au revoir"]]


async def sum():
    await asyncio.gather(*ll)


asyncio.get_event_loop().run_until_complete(sum())
