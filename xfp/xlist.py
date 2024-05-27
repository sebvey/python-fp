# from _typeshed import SupportsRichComparison # not available ...

from typing import Iterable, Iterator, Callable, Any
from collections.abc import Iterable as ABCIterable


# Element type alias
type E = Any


def _id[E](e: E) -> E:
    return e


class Xlist[T: E]:
    def __init__(self, iterable: Iterable[T]) -> None:
        match iterable:
            case ABCIterable():
                self.__data = list(iterable)
            case _:
                raise TypeError(
                    f"'{type(iterable).__name__}' not allowed for Xlist constructor"
                )

    def __iter__(self) -> Iterator[T]:
        return iter(self.__data)

    def __eq__(self, other: object) -> bool:
        match other:
            case ABCIterable():
                return [e for e in self] == [e for e in other]
            case _:
                return False

    def __len__(self) -> int:
        return len(self.__data)

    def head(self) -> T:
        if len(self) <= 0:
            raise IndexError("<head> operation not allowed on empty list")
        return self.__data[0]

    def tail(self) -> "Xlist[T]":
        if len(self) <= 0:
            raise IndexError("<tail> operation not allowed on empty list")
        return Xlist(self.__data[1:])

    def map(self, f: Callable[[T], E]) -> "Xlist[E]":
        return Xlist([f(el) for el in self])

    def filter(self, predicate: Callable[[T], bool]) -> "Xlist[T]":
        return Xlist([el for el in self if predicate(el)])

    def foreach(self, statement: Callable[[T], None]) -> None:
        (statement(e) for e in self)

    def flatten(self) -> "Xlist[E]":
        return Xlist([inner for e in self if isinstance(e, ABCIterable) for inner in e])

    def flat_map(self, f: Callable[[T], Iterable[E]]) -> "Xlist[E]":
        return self.map(f).flatten()

    def min(self, key: Callable[[T], E] = _id) -> T:
        return min(self, key=key)

    def max(self, key: Callable[[T], E] = _id) -> T:
        return max(self, key=key)

    def sorted(self, key: Callable[[T], E] = _id, reverse: bool = False) -> "Xlist[T]":
        return Xlist(sorted(self, key=key, reverse=reverse))

    def reverse(self) -> "Xlist[T]":
        data: list[T] = self.__data.copy()
        data.reverse()
        return Xlist(data)

    def foldLeft(self, zero: E) -> Callable[[Callable[[E, T], E]], E]:
        def inner(f: Callable[[E, T], E]) -> E:
            acc: E = zero
            for e in self:
                acc = f(acc, e)
            return acc

        return inner

    def foldRight(self, zero: E) -> Callable[[Callable[[T, E], E]], E]:
        def inner(f: Callable[[T, E], E]) -> E:
            return self.reverse().foldLeft(zero)(lambda e, t: f(t, e))

        return inner

    def fold(self, zero: T) -> Callable[[Callable[[T, T], E]], E]:
        def inner(f: Callable[[T, T], E]) -> E:
            return self.foldLeft(zero)(f)

        return inner

    def reduce(self, f: Callable[[T, T], T]) -> T:
        if len(self) <= 0:
            raise IndexError("<reduce> operation not allowed on empty list")
        return self.tail().fold(self.head())(f)
