import asyncio
from dataclasses import dataclass
from typing import override, Iterable
from xfp.a.async_handler import AsyncHandler

from xfp.functions import XFunc, tupled2


@dataclass
class SimpleAsyncHandler(AsyncHandler):
    """Async Handler that processes elements using their asynchronicity.

    Handles async function, and makes good use of cpu usage.

    ## Usage

    ```python
        from xfp import Xlist
        import asyncio

        sequential_list = Xlist([1, 2, 3, 4, 5], async_handler=SimpleAsyncHandler())

        async def multiply(i: int):
            await asyncio.sleep(0.01)
            return i*i

        # Should take ~= 0.01 second
        assert sequential_list.map(multiply) == Xlist([1, 4, 9, 16, 25])
    ```
    """

    @override
    def map[X, Y](self, f: XFunc[[X], Y], xs: Iterable[X]) -> Iterable[Y]:
        @XFunc.from_async
        async def h() -> Iterable[Y]:
            return await asyncio.gather(*map(f, xs))

        return h.collect()

    @override
    def reduce[X](self, f: XFunc[[X, X], X], xs: Iterable[X]) -> X:
        """Specific implementation of the reduce operation."""
        lxs = list(xs)
        length = len(lxs)

        @XFunc.from_async
        async def step(sublist: list[X]) -> list[X]:
            return await asyncio.gather(
                *map(tupled2(f), zip(sublist[::2], sublist[1::2]))
            )

        if length == 1:
            return lxs[0]
        elif length % 2 == 0:
            return self.reduce(f, step.collect(lxs))
        else:
            return self.reduce(f, step.collect(lxs[1:]) + [lxs[0]])
