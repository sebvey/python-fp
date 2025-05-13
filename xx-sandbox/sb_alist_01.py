from xfp.a import Alist, Afunc, funcbox

import trio


type Sec = int


@Afunc
async def double(i: int) -> int:
    await trio.sleep(2)
    return i * 2


@Afunc
async def to_string(i: int) -> str:
    return str(i)


@Afunc
async def show(i: int) -> None:
    print(f"Show -> Got {i}")


iter = range(10)


async def my_task() -> None:
    await Alist.from_iterable(iter, 2).map(double).foreach(show)
    result = await Alist.from_iterable(iter).map(double).map(to_string)
    result.foreach(print)


### MAIN ###########


async def main() -> None:
    async with trio.open_nursery() as n:
        n.start_soon(my_task)
        await trio.sleep(0.5)
        n.start_soon(funcbox.background_tick, 12)


trio.run(main)
