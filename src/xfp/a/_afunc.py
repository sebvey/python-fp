from __future__ import annotations
from typing import Awaitable

from xfp import Xresult, XRBranch
from xfp.functions import F1

from ._typing import AwaitableXR, CoFunc, CoFuncXR


# Afunc = Awaitable Function:
# - meant for functions that DOES NOT RAISE (if raising is expected, use ARfunc.from_unsafe instead)

# TODO - curry embryo (start with two args to one)


class Afunc[**P, X]:
    def __init__(self, cofunc: CoFunc[P, X]) -> None:
        self._cofunc = cofunc

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Awaitable[X]:
        return self.cofunc(*args, **kwargs)

    @staticmethod
    def from_safe(func: F1[P, X]) -> Afunc[P, X]:
        async def cofunc(*args: P.args, **kwargs: P.kwargs) -> Awaitable[X]:
            return func(*args, **kwargs)

        return Afunc(cofunc)

    # TODO - map another Afunc, with only one arg
    # TODO - map another ARfunc, with only one arg


class ARfunc[**P, L, R]:
    def __init__(self, cofunc: CoFuncXR[P, L, R]) -> None:
        self._cofunc = cofunc

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> AwaitableXR[L, R]:
        return self.cofunc(*args, **kwargs)

    @staticmethod
    def from_unsafe(func: F1[P, R]) -> ARfunc[P, Exception, R]:
        async def cofunc(*args: P.args, **kwargs: P.kwargs) -> Xresult[Exception, R]:
            try:
                return Xresult(func(*args, **kwargs), XRBranch.RIGHT)
            except Exception as e:
                return Xresult(e, XRBranch.LEFT)

        return ARfunc(cofunc)
