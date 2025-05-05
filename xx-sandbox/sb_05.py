import random
from xfp import Xresult, XRfunc, Xfunc, Alist
import trio
from pprint import pprint

type Sec = int


@Xfunc
async def random_delay_and_double(i: int) -> int:
    waiting_time = random.randrange(1000, 10000) / 1000
    await trio.sleep(waiting_time)
    print(f"LOG: {i} doubled successfully")
    return i * 2


@XRfunc
async def str_negative(i: int) -> Xresult[ValueError, str]:
    return Xresult.right(-i) if i >= 0 else Xresult.left(ValueError("Negative int"))


# TODO - Alist is for list of X
# TODO -> ARlist for list of Xresult


async def functional_main() -> None:
    result = await (
        Alist.from_iterable([-1, 2, 3, 4, 5, 6, -7])
        .map(random_delay_and_double)
        .map(str_negative)
    )
    pprint(result)


async def background_tick(duration: Sec) -> None:
    n = 0
    while n <= duration:
        print(f"BACKGROUND TICK - {n}")
        n += 1
        await trio.sleep(1)


async def main() -> None:
    async with trio.open_nursery() as nursery:
        nursery.start_soon(background_tick, 10)
        nursery.start_soon(functional_main)


trio.run(main)
