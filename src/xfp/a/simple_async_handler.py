import asyncio
from dataclasses import dataclass
import functools
from typing import override, Iterable
from xfp.a.async_handler import AsyncHandler

from xfp.functions import XF1, XFunc


@dataclass
class SimpleAsyncHandler(AsyncHandler):
    @override
    def ap[X, Y](
        self, async_process: Iterable[XF1[[X], Y]]
    ) -> XFunc[[Iterable[X]], Iterable[Y]]:
        async def h(iter: Iterable[X]) -> Iterable[Y]:
            return await asyncio.gather(
                *(map((lambda fel: XFunc(fel[0])(fel[1])), zip(async_process, iter)))
            )

        return XFunc(h)

    @override
    def reduce[X](self, f: XF1[[X, X], X], xs: Iterable[X]) -> X:
        return functools.reduce(XFunc(f).collect, xs)
