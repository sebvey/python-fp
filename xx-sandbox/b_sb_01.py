from xfp.a import Alist
from xfp import Xlist

import trio


type Sec = int


async def double(i: int) -> int:
    await trio.sleep(2)
    return i * 2


async def to_string(i: int) -> str:
    return str(i)


async def show(i: int) -> None:
    print(f"Show -> Got {i}")


iter = range(10)


async def my_task() -> None:
    await Alist.from_iterable(iter, 2).map(double).foreach(show)
    result: Xlist = await Alist.from_iterable(iter).map(double).map(to_string)
    result.foreach(print)


### MAIN ###########


async def background_tick(duration: Sec) -> None:
    n = 0
    while n <= duration:
        print(f"BACKGROUND TICK - {n}")
        n += 1
        await trio.sleep(1)


async def main() -> None:
    async with trio.open_nursery() as n:
        n.start_soon(my_task)
        await trio.sleep(0.5)
        n.start_soon(background_tick, 20)


trio.run(main)
