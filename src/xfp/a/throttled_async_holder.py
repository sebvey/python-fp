import asyncio
from dataclasses import dataclass
import functools
from typing import override, Iterable
from xfp import tupled
from xfp.a.async_holder import AsyncHolder

from xfp.functions import XF1, XFunc


@dataclass
class ThrottledAsyncHolder(AsyncHolder):
    throttle: int

    @override
    def ap[X, Y](
        self, async_process: Iterable[XF1[[X], Y]]
    ) -> XFunc[[Iterable[X]], Iterable[Y]]:
        async def h(iter: Iterable[X]) -> Iterable[Y]:
            materialized = list(iter)
            res = []
            for i in range(0, len(materialized), self.throttle):
                subrange: Iterable[X] = materialized[i : i + self.throttle]
                ops = list(
                    map(
                        tupled(lambda f, el: XFunc(f)(el)), zip(async_process, subrange)
                    )
                )
                async_res = await asyncio.gather(*ops)
                res = res + async_res
            return res

        return XFunc(h)

    @override
    def reduce[X](self, f: XF1[[X, X], X], xs: Iterable[X]) -> X:
        return functools.reduce(XFunc(f).collect, xs)
