from dataclasses import dataclass
from xfp.a.functions import AF1
from xfp.functions import F1


@dataclass(frozen=True)
class AFunc[**X, Y]:
    f: AF1[X, Y]

    async def __call__(self, *args: X.args, **kwargs: X.kwargs) -> Y:
        """Uses the underlying f.__call__."""
        return await self.f(*args, **kwargs)

    def map[U](self, g: F1[[Y], U]) -> "AFunc[X, U]":
        async def h(*args: X.args, **kwargs: X.kwargs) -> U:
            y = await self(*args, **kwargs)
            return g(y)

        return AFunc(h)

    def contramap[**T, XX](self: "AFunc[[XX], Y]", g: F1[T, XX]) -> "AFunc[T, Y]":
        from xfp.functions import XFunc

        return XFunc(g).async_map(self)

    def async_map[U](self, g: AF1[[Y], U]) -> "AFunc[X, U]":
        async def h(*args: X.args, **kwargs: X.kwargs) -> U:
            y = await self(*args, **kwargs)
            return await g(y)

        return AFunc(h)

    def async_contramap[**T, XX](
        self: "AFunc[[XX], Y]", g: AF1[T, XX]
    ) -> "AFunc[T, Y]":
        return AFunc(g).async_map(self)
