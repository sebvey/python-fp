import asyncio
from dataclasses import dataclass
import functools
from typing import override, Iterable
from xfp.a import SequentialHolder
from xfp.a.async_holder import AsyncHolder

from xfp.functions import XF1, XFunc
import itertools


@dataclass
class ThrottledAsyncHolder(AsyncHolder):
    throttle: int

    @override
    def ap[X, Y](
        self, async_process: Iterable[XF1[[X], Y]]
    ) -> XFunc[[Iterable[X]], Iterable[Y]]:
        from xfp import Xlist

        async def h(iter: Iterable[X]) -> Iterable[Y]:
            async def chunk_op(iterf: Iterable[tuple[X, XF1[[X], Y]]]) -> Iterable[Y]:
                return await asyncio.gather(*[XFunc(f)(el) for el, f in iterf])

            return Xlist(
                itertools.batched(zip(iter, async_process), self.throttle),
                SequentialHolder(),
            ).flat_map(chunk_op)

        return XFunc(h)

    @override
    def reduce[X](self, f: XF1[[X, X], X], xs: Iterable[X]) -> X:
        return functools.reduce(XFunc(f).collect, xs)
