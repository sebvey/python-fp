from __future__ import annotations
from typing import Any, Awaitable, Callable, Generator, overload, Coroutine

from xfp import Xresult, XRBranch

from ._typing import CoFunc, CoFuncXR


class Afunc[**P, R]:
    def __init__(self, cofunc: CoFunc[P, R]) -> None:
        self._cofunc = cofunc

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Acoroutine[R]:
        return Acoroutine(self._cofunc(*args, **kwargs))

    @staticmethod
    def from_safe(func: Callable[P, R]) -> Afunc[P, R]:
        async def cofunc(*args: P.args, **kwargs: P.kwargs) -> Awaitable[R]:
            return func(*args, **kwargs)

        return Afunc(cofunc)


class Acoroutine[R](Coroutine[Any, Any, R]):
    def __init__(self, coroutine: Coroutine[Any, Any, R]) -> None:
        self._coroutine = coroutine

    def __await__(self) -> Generator[Any, Any, R]:
        return self._coroutine.__await__()

    def send(self, value) -> Any:
        return self._coroutine.send(value)

    def throw(self, value) -> Any:
        return self._coroutine.throw(value)

    def close(self) -> None:
        return self._coroutine.close()

    @overload
    def pipe[Ro](self, afunc: Afunc[[R], Ro]) -> Acoroutine[Ro]:
        "pipe an Afunc"
        ...

    @overload
    def pipe[Lo, Ro](self, arfunc: ARfunc[[R], Lo, Ro]) -> ARcoroutine[Lo, Ro]:
        "pipe an ARfunc"
        ...

    def pipe[Lo, Ro](
        self, aarfunc: Afunc[[R], Ro] | ARfunc[[R], Lo, Ro]
    ) -> Acoroutine[Ro] | ARcoroutine[Lo, Ro]:
        async def cofunc() -> Ro:
            return await aarfunc(await self._coroutine)

        if isinstance(aarfunc, Afunc):
            return Acoroutine(cofunc())
        elif isinstance(aarfunc, ARfunc):
            return ARcoroutine(cofunc())
        else:
            raise ValueError("pipe only Afunc or ARfunc")


class ARfunc[**P, L, R]:
    def __init__(self, cofunc: CoFuncXR[P, L, R]) -> None:
        self._cofunc = cofunc

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> ARcoroutine[L, R]:
        return ARcoroutine(self._cofunc(*args, **kwargs))

    @staticmethod
    def from_unsafe(func: Callable[P, R]) -> ARfunc[P, Exception, R]:
        async def cofunc(*args: P.args, **kwargs: P.kwargs) -> Xresult[Exception, R]:
            try:
                return Xresult(func(*args, **kwargs), XRBranch.RIGHT)
            except Exception as e:
                return Xresult(e, XRBranch.LEFT)

        return ARfunc(cofunc)


class ARcoroutine[L, R](Coroutine[Any, Any, Xresult[L, R]]):
    def __init__(self, coroutine: Coroutine[Any, Any, Xresult[L, R]]) -> None:
        self._coroutine = coroutine

    def __await__(self) -> Generator[Any, Any, Xresult[L, R]]:
        return self._coroutine.__await__()

    def send(self, value) -> Any:
        return self._coroutine.send(value)

    def throw(self, value) -> Any:
        return self._coroutine.throw(value)

    def close(self) -> None:
        return self._coroutine.close()

    def map_right[Ro](self, afunc: Afunc[[R], Ro]) -> ARcoroutine[L, Ro]:
        async def cofunc() -> Xresult[L, Ro]:
            result: Xresult[L, R] = await self
            if result.is_right():
                return Xresult(await afunc(result.value), XRBranch.RIGHT)
            return result

        return ARcoroutine(cofunc())

    def map[Ro](self, afunc: Afunc[[R], Ro]) -> ARcoroutine[L, Ro]:
        return self.map_right(afunc)

    def map_left[Lo](self, afunc: Afunc[[L], Lo]) -> ARcoroutine[Lo, R]:
        async def cofunc() -> Xresult[Lo, R]:
            result: Xresult[L, R] = await self
            if result.is_left():
                return Xresult(await afunc(result.value), XRBranch.LEFT)
            return result

        return ARcoroutine(cofunc())

    def flat_map_right[Lo, Ro](
        self, arfunc: ARfunc[[R], Lo, Ro]
    ) -> ARcoroutine[L | Lo, Ro]:
        async def cofunc() -> Xresult[L | Lo, Ro]:
            result: Xresult[L, R] = await self
            if result.is_right():
                return await arfunc(result.value)
            return result

        return ARcoroutine(cofunc())

    def flat_map[Lo, Ro](self, arfunc: ARfunc[[R], Lo, Ro]) -> ARcoroutine[L | Lo, Ro]:
        return self.flat_map_right(arfunc)

    def flat_map_left[Lo, Ro](
        self, arfunc: ARfunc[[L], Lo, Ro]
    ) -> ARcoroutine[Lo, R | Ro]:
        async def cofunc() -> Xresult[Lo, R | Ro]:
            result: Xresult[L, R] = await self
            if result.is_left():
                return await arfunc(result.value)
            return result

        return ARcoroutine(cofunc())

    def recover[Ro](self, afunc: Afunc[[L], Ro]) -> Acoroutine[R | Ro]:
        """
        if LEFT -> recover value with effectless function
        if RIGHT -> simply 'extract' value
        => output is no more a Xresult but a standard value
        TODO: arguable choice to switch to a Acoroutine
        """

        async def cofunc() -> R | Ro:
            result = await self
            if result.is_left():
                return await afunc(result.value)
            return result.value

        return Acoroutine(cofunc())

    def pipe[Ro](self, afunc: Afunc[[Xresult[L, R]], Ro]) -> Acoroutine[Ro]:
        async def cofunc() -> Ro:
            return await afunc(await self._coroutine)

        return Acoroutine(cofunc())
