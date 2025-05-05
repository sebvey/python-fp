from __future__ import annotations
from typing import Any, Callable, Generator, overload

from xfp import Xtry, Xresult, XRBranch
from ._typing import PyCoXR, PyCo

# TODO - currying est juste un embryon pour voir si ça marche
# TODO - typing bien foireux, particulièrement en terme d'argument. J'ai peur que ce soit hard...
# TODO - Xfunc / XRfunc, en fait faut les appeler Afunc / ARfunc (async func)


class Xfunc[**P, X]:
    def __init__(self, cofunc: Callable[P, PyCo[X]]) -> None:
        self._cofunc: Callable[P, PyCo[X]] = cofunc

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Xcoroutine[X]:
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

    @overload
    def pipe[P, LO, RO](self, xrfunc: XRfunc[P, LO, RO]) -> XRcoroutine[LO, RO]:
        "pipe an XRfunc."
        ...

    @overload
    def pipe[P, RO](self, xfunc: Xfunc[P, RO]) -> Xcoroutine[RO]:
        "pipe an Xfunc."
        ...

    def pipe[P, LO, RO](
        self, xxrfunc: Xfunc[P, RO] | XRfunc[P, LO, RO]
    ) -> Xcoroutine[RO] | XRcoroutine[LO, RO]:
        async def cofunc() -> RO:
            result: X = await self._coroutine
            return await xxrfunc(result)

        if isinstance(xxrfunc, Xfunc):
            return Xcoroutine(cofunc())
        elif isinstance(xxrfunc, XRfunc):
            return XRcoroutine(cofunc())


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
            else:
                return result

        return XRcoroutine(cofunc())

    def map[**P, X](self, xfunc: Xfunc[P, X]) -> XRcoroutine[L, X]:
        return self.map_right(xfunc)

    def map_left[**P, X](self, xfunc: Xfunc[P, X]) -> XRcoroutine[X, R]:
        async def cofunc() -> Xresult[X, R]:
            result: Xresult[L, R] = await self
            if result.is_left():
                return Xresult(await xfunc(result.value), XRBranch.LEFT)
            else:
                return result

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

    def pipe[P, X](self, xfunc: Xfunc[P, X]) -> Xcoroutine[X]:
        async def cofunc() -> X:
            return await xfunc(await self._coroutine)

        return Xcoroutine(cofunc())
