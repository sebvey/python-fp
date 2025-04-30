from typing import Any, Never
from xfp import Xresult, Xtry, XRfunc
from xfp.xfunc import xrf
import anyio
import math

type Sec = int


@XRfunc
async def parse(s: str) -> Xresult[ValueError, int]:
    await anyio.sleep(0.5)
    return Xtry.from_unsafe(lambda: int(s))


@XRfunc
async def recover(_: ValueError) -> Xresult[Never, int]:
    await anyio.sleep(0.5)
    return Xtry.Success(42)


@XRfunc
async def factorial(i: int) -> Xresult[ValueError, int]:
    await anyio.sleep(0.5)
    return Xtry.from_unsafe(lambda: math.factorial(i))


async def print_repr(x: Any) -> None:
    print(f"Got {repr(x)}")


async def functional_main() -> None:
    await parse("6").flat_map(factorial).flat_map(xrf.print)
    await (
        parse("hello").flat_map(factorial).foreach_left(print_repr)
        # .flat_map_left(XRfunc.from_unsafe(lambda e: print(repr(e))))
    )
    await parse("hello").flat_map_left(recover).flat_map(factorial).foreach(xrf.print)


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
