from typing import Never
from xfp import Xresult, Xtry, Xeffect, Xlist
import trio
import math


@Xeffect
async def parse(s: str) -> Xresult[ValueError, int]:
    await trio.sleep(0.1)
    return Xtry.from_unsafe(lambda: int(s))


@Xeffect
async def recover(e: ValueError) -> Xresult[Never, int]:
    await trio.sleep(0.1)
    return Xtry.Success(42)


@Xeffect
async def factorial(i: int) -> Xresult[ValueError, int]:
    await trio.sleep(0.1)
    return Xtry.from_unsafe(lambda: math.factorial(i))


async def main() -> None:
    result_1 = await parse("6").map(factorial)
    result_2 = await parse("hello").map(factorial)
    result_3 = await parse("hello").map_left(recover).map(factorial)

    Xlist([result_1, result_2, result_3]).foreach(print)


# async def background() -> None:
#     for i in range()

trio.run(main)
