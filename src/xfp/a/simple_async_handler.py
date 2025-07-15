import asyncio
from dataclasses import dataclass
import functools
from typing import override, Iterable
from xfp.a.async_handler import AsyncHandler

from xfp.functions import XFunc


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
        return functools.reduce(f.collect, xs)
