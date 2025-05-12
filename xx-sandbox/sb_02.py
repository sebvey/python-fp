from typing import Any
from xfp import Xresult, Xtry
from xfp.a import ARfunc, Afunc
import trio
import math

type Sec = int


@ARfunc
async def parse(s: str) -> Xresult[ValueError, int]:
    await trio.sleep(0.5)
    return Xtry.from_unsafe(lambda: int(s))


@Afunc
async def double(i: int) -> int:
    return i * 2


@ARfunc
async def factorial(i: int) -> Xresult[ValueError, int]:
    await trio.sleep(0.5)
    return Xtry.from_unsafe(lambda: math.factorial(i))


async def print_repr(x: Any) -> None:
    print(f"Got {repr(x)}")


async def functional_main() -> None:
    await parse("6").map_right(double).flat_map(factorial).map(Afunc.from_safe(print))


async def background_tick(duration: Sec) -> None:
    n = 0
    while n <= duration:
        print(f"BACKGROUND TICK - {n}")
        n += 1
        await trio.sleep(1)


async def main() -> None:
    async with trio.open_nursery() as nursery:
        nursery.start_soon(background_tick, 3)
        nursery.start_soon(functional_main)


trio.run(main)
