import random
from xfp import Xresult, XRfunc, Xfunc
from xfp.xfunc import xcurry2
import trio
from pprint import pprint


@xcurry2
async def product(fac: int, x: int) -> None:
    print(f"{fac * x}")


class RandomError(Exception):
    pass


@XRfunc
async def api_call(i: int) -> Xresult[RandomError, str]:
    waiting_time = random.randrange(500, 2000) / 1000
    await trio.sleep(waiting_time)

    print(f"API_CALL({i}) -> DONE")

    if random.randrange(0, 10) < 6:
        return Xresult.right(str(i))
    else:
        return Xresult.left(RandomError(f"Random error for i={i}"))


@Xfunc
async def prettify(s: str) -> str:
    return f"API_CALL SUCCESSFULLY ANSWERED: {s}"


async def process(i: int) -> Xresult[RandomError, None]:
    return await api_call(i).map(prettify)


async def async_map[X, L, R](
    it: list[X], xrfunc: XRfunc[X, L, R]
) -> list[Xresult[L, R]]:
    indexed_it: list[tuple[int, X]] = [(id, el) for id, el in enumerate(it)]
    results: list[tuple[int, Xresult[L, R]]] = []

    async def bad_cowboy(id: int, el: X) -> None:
        results.append((id, await xrfunc(el)))

    async with trio.open_nursery() as tg:
        for indexed_el in indexed_it:
            tg.start_soon(bad_cowboy, indexed_el[0], indexed_el[1])

    results.sort(key=lambda e: e[0])
    return [r[1] for r in results]


async def main() -> None:
    my_list = [1, 2, 3, 4, 5, 6, 7, 8]
    results = await async_map(my_list, process)

    pprint(results)


trio.run(main)
