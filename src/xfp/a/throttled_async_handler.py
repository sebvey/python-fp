import asyncio
from dataclasses import dataclass
from typing import override, Iterable
from xfp.a import SequentialHandler, SimpleAsyncHandler
from xfp.a.async_handler import AsyncHandler

from xfp.functions import XFunc
import itertools


@dataclass
class ThrottledAsyncHandler(AsyncHandler):
    """Async Handler that processes elements using their asynchronicity.

    However, computes at most `throttle` elements at the same time.
    Use this when you are using services with a calling rate (ie. API).

    ## Usage

    ```python
        from xfp import Xlist
        import asyncio

        sequential_list = Xlist([1, 2, 3, 4, 5, 6], async_handler=ThrottledAsyncHandler(2))

        async def multiply(i: int):
            await asyncio.sleep(0.01)
            return i*i

        # Should take ~= 0.01 second * 6 elements / 2 throttle == 0.03 second
        assert sequential_list.map(multiply) == Xlist([1, 4, 9, 16, 25, 36])
    ```
    """

    throttle: int

    @override
    def map[X, Y](self, f: XFunc[[X], Y], xs: Iterable[X]) -> Iterable[Y]:
        from xfp import Xlist

        @XFunc.from_async
        async def h(iter: tuple[X, ...]) -> Iterable[Y]:
            return await asyncio.gather(*map(f, iter))

        return Xlist(
            itertools.batched(xs, self.throttle), async_handler=SequentialHandler()
        ).flat_map(h)

    @override
    def reduce[X](self, f: XFunc[[X, X], X], xs: Iterable[X]) -> X:
        from xfp import Xlist

        if len(list(xs)) == 1:
            return list(xs)[0]
        else:
            return self.reduce(
                f,
                Xlist(
                    itertools.batched(xs, self.throttle),
                    async_handler=SequentialHandler(),
                ).map(lambda xxs: SimpleAsyncHandler().reduce(f, xxs)),
            )
