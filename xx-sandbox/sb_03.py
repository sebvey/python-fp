from typing import Any
from xfp import Xresult, Xtry
from xfp.a import Afunc, ARfunc, funcbox
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


@Afunc
async def print_repr(x: Any) -> None:
    print(f"Got {repr(x)}")


async def functional_main() -> None:
    await double(3).pipe(factorial).map_left(funcbox.print).map_right(funcbox.print)
    await factorial(3).pipe(funcbox.print)


async def background_tick(duration: Sec) -> None:
    n = 0
    while n <= duration:
        print(f"BACKGROUND TICK - {n}")
        n += 1
        await trio.sleep(1)


async def main() -> None:
    async with trio.open_nursery() as nursery:
        nursery.start_soon(background_tick, 6)
        nursery.start_soon(functional_main)


trio.run(main)
