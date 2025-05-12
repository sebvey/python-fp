from typing import Any, Never
from xfp import Xresult, Xtry
from xfp.a import ARfunc, Afunc
from xfp.xfunc import funcbox
import trio
import math

type Sec = int


@ARfunc
async def parse(s: str) -> Xresult[ValueError, int]:
    await trio.sleep(0.5)
    return Xtry.from_unsafe(lambda: int(s))


@ARfunc
async def recover(_: ValueError) -> Xresult[Never, int]:
    await trio.sleep(0.5)
    return Xtry.Success(42)


@ARfunc
async def factorial(i: int) -> Xresult[ValueError, int]:
    await trio.sleep(0.5)
    return Xtry.from_unsafe(lambda: math.factorial(i))


@Afunc
async def print_repr(x: Any) -> None:
    print(f"Got {repr(x)}")


async def functional_main() -> None:
    await parse("6").flat_map(factorial).flat_map(funcbox.print_xr)
    await (
        parse("hello").flat_map(factorial).map_left(print_repr)
        # .flat_map_left(ARfunc.from_unsafe(lambda e: print(repr(e))))
    )
    await (
        parse("hello").flat_map_left(recover).flat_map(factorial).pipe(funcbox.print_xr)
    )


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
