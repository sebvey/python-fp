from typing import Iterable, Iterator, Callable, Any, List
from collections.abc import Iterable as ABCIterable

# flat element type (no nested Xlist)
# TODO : to be extended in the future
type F = (int | str | float)

# element type, one possible 'nested level'
type E = (F | "Xlist[F]" | List[F])


def _id[E](e: E) -> E:
    return e


class Xlist[T: E]:

    def __init__(self, iterable: Iterable[T]) -> None:

        self.__data = list(iterable)

    def __iter__(self) -> Iterator[T]:
        return iter(self.__data)

    def __eq__(self, other: object) -> bool:
        match other:
            case ABCIterable():
                return [e for e in self] == [e for e in other]
            case _:
                return False

    def map(self, f: Callable[[T], E]) -> "Xlist[E]":
        return Xlist([f(el) for el in self])

    def filter(self, predicate: Callable[[T], bool]) -> "Xlist[T]":
        return Xlist([el for el in self if predicate(el)])

    def foreach(self, statement: Callable[[T], None]) -> None:
        for el in self:
            statement(el)

    def flatten(self) -> "Xlist[E]":
        return Xlist([inner for e in self if isinstance(e, ABCIterable) for inner in e])

    def flatMap(self, f: Callable[[T], E]) -> "Xlist[E]":
        return self.map(f).flatten()

    # should be something like key: Callable[[T], SupportsRichComparison]
    def min(self, key: Callable[[T], Any] = _id):
        return min(self, key=key)

    def max(self, key: Callable[[T], Any] = _id):
        return max(self, key=key)

    def sorted(
        self, key: Callable[[T], Any] = _id, reverse: bool = False
    ) -> "Xlist[T]":
        return Xlist(sorted(self, key=key, reverse=reverse))
