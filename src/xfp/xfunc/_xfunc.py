from __future__ import annotations
from typing import Any, Callable, Generator

from xfp import Xtry, Xresult, XRBranch
from ._typing import PyCoXR, PyCo

# TODO - IN PROGRESS - pipe()
# TODO - et le currying dans tout ça ? pronostic, ça va piquer
# TODO - typing bien foireux, particulièrement en terme d'argument. J'ai peur que ce soit hard...


class Xfunc[**P, X]:
    def __init__(self, cofunc: Callable[P, PyCo[X]]) -> None:
        self._cofunc: Callable[P, PyCo[X]] = cofunc

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> PyCo[X]:
        return Xcoroutine(self._cofunc(*args, **kwargs))

    @classmethod
    def from_safe(cls, func: Callable[P, X]) -> Xfunc[P, X]:
        async def cofunc(*args: P.args, **kwargs: P.kwargs) -> X:
            return func(*args, **kwargs)

        return Xfunc(cofunc)


class Xcoroutine[X]:
    def __init__(self, coroutine: PyCo[X]) -> None:
        self._coroutine = coroutine

    def __await__(self) -> Generator[Any, Any, X]:
        return self._coroutine.__await__()

    # TODO - pipe with two implems : pipe(Xfunc) et pipe(XRfunc) - ça va être golo
    def pipe[P, XO](self, xfunc: Xfunc[P, X]) -> Xcoroutine[XO]:
        async def cofunc() -> XO:
            result: X = await self._coroutine
            return await xfunc(result)

        return Xfunc(cofunc)


class XRfunc[**P, L, R]:
    def __init__(self, cofunc: Callable[P, PyCoXR[L, R]]) -> None:
        self._cofunc: Callable[P, PyCoXR[L, R]] = cofunc

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> XRcoroutine[L, R]:
        return XRcoroutine(self._cofunc(*args, **kwargs))

    @classmethod
    def from_unsafe(cls, func: Callable[P, R]) -> XRfunc[P, Exception, R]:
        async def cofunc(*args: P.args, **kwargs: P.kwargs) -> Xresult[Exception, R]:
            try:
                return Xtry.Success(func(*args, **kwargs))
            except Exception as e:
                return Xtry.Failure(e)

        return XRfunc(cofunc)


class XRcoroutine[L, R]:
    def __init__(self, coroutine: PyCoXR[L, R]) -> None:
        self._coroutine = coroutine

    def __await__(self) -> Generator[Any, Any, Xresult[L, R]]:
        return self._coroutine.__await__()

    def map_right[**P, X](self, xfunc: Xfunc[P, X]) -> XRcoroutine[L, X]:
        async def cofunc() -> Xresult[L, X]:
            result: Xresult[L, R] = await self
            if result.is_right():
                return Xresult(await xfunc(result.value), XRBranch.RIGHT)

        return XRcoroutine(cofunc())

    def map[**P, X](self, xfunc: Xfunc[P, X]) -> XRcoroutine[L, X]:
        return self.map_right(xfunc)

    def map_left[**P, X](self, xfunc: Xfunc[P, X]) -> XRcoroutine[X, R]:
        async def cofunc() -> Xresult[X, R]:
            result: Xresult[L, R] = await self
            if result.is_left():
                return Xresult(await xfunc(result.value), XRBranch.LEFT)

        return XRcoroutine(cofunc())

    def flat_map_right[PO, LO, RO](
        self, xrfunc: XRfunc[PO, LO, RO]
    ) -> XRcoroutine[L | LO, RO]:
        async def cofunc() -> Xresult[L | LO, RO]:
            result: Xresult[L, R] = await self
            if result.is_right():
                return await xrfunc(result.value)
            return result

        return XRcoroutine(cofunc())

    def flat_map_left[PO, LO, RO](
        self, xrfunc: XRfunc[PO, LO, RO]
    ) -> XRcoroutine[LO, R | RO]:
        async def func() -> Xresult[LO, R]:
            result: Xresult[L, R] = await self
            if result.is_left():
                return await xrfunc(result.value)
            return result

        return XRcoroutine(func())

    def flat_map[PO, LO, RO](
        self, xrfunc: XRfunc[PO, LO, RO]
    ) -> XRcoroutine[L | LO, RO]:
        "Alias for .flat_map_right()"
        return self.flat_map_right(xrfunc)

    # TODO - switch to Xfunc - mais bon niveau runtime c'est équivalent ...
    def foreach_right(self, cofunc: Callable[[R], PyCo[Any]]) -> PyCo[None]:
        "Do Xfunc to the underlying value if self is a RIGHT"

        async def new_cofunc() -> None:
            result: Xresult[L, R] = await self
            if result.is_right():
                return await cofunc(result.value)

        return XRcoroutine(new_cofunc())

    # TODO - idem
    def foreach_left(self, cofunc: Callable[[L], PyCo[Any]]) -> PyCo[None]:
        "Do the async statement procedure to the underlying value if self is a LEFT"

        async def new_cofunc() -> None:
            result: Xresult[L, R] = await self
            if result.is_left():
                return await cofunc(result.value)

        return XRcoroutine(new_cofunc())

    # TODO - idem
    def foreach(self, cofunc: Callable[[R], PyCo[Any]]) -> PyCo[None]:
        "Alias for .foreach_right()"
        return self.foreach_right(cofunc)
