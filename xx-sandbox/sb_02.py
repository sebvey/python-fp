from typing import Any
from xfp import Xresult, Xtry, XRfunc, Xfunc
import anyio
import math

type Sec = int


@XRfunc
async def parse(s: str) -> Xresult[ValueError, int]:
    await anyio.sleep(0.5)
    return Xtry.from_unsafe(lambda: int(s))


@Xfunc
async def double(i: int) -> int:
    return i * 2


@XRfunc
async def factorial(i: int) -> Xresult[ValueError, int]:
    await anyio.sleep(0.5)
    return Xtry.from_unsafe(lambda: math.factorial(i))


async def print_repr(x: Any) -> None:
    print(f"Got {repr(x)}")


async def functional_main() -> None:
    await parse("6").map_right(double).flat_map(factorial).map(Xfunc.from_safe(print))


async def background_tick(duration: Sec) -> None:
    n = 0
    while n <= duration:
        print(f"BACKGROUND TICK - {n}")
        n += 1
        await anyio.sleep(1)


async def main() -> None:
    async with anyio.create_task_group() as tg:
        tg.start_soon(background_tick, 6)
        tg.start_soon(functional_main)


anyio.run(main)
