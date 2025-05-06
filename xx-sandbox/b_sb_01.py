from xfp.b import Blist
import trio


async def double(i: int) -> int:
    await trio.sleep(2)
    return i * 2


async def show(i: int) -> None:
    print(f"Show -> Got {i}")


iter = range(10)


async def my_task() -> None:
    await Blist.from_iter(iter).map(double).foreach(show)


async def main() -> None:
    async with trio.open_nursery() as n:
        n.start_soon(my_task)


trio.run(main)
