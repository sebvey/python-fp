from typing import Callable, Iterable, Iterator, Any
from collections.abc import Iterable as ABCIterable
from .utils import E


class Xiter[X: E]:
    def __init__(self, iterable: Iterable[X]) -> None:
        match iterable:
            case ABCIterable():
                self.iter: Iterator = iter(iterable)
            case _:
                raise TypeError("Xiter must be constructed from an iterable")

    def __iter__(self) -> Iterator[X]:
        return self.iter

    def __repr__(self) -> str:
        return repr(self.iter)

    def map(self, f: Callable[[X], E]) -> "Xiter[E]":
        return Xiter(map(f, self))

    def flatten(self) -> "Xiter[E]":
        return Xiter(inner for e in self if isinstance(e, ABCIterable) for inner in e)

    def flat_map(self, f: Callable[[X], Iterable[E]]) -> "Xiter[E]":
        return Xiter(el for iterable in self.map(f) for el in iterable)

    def filter(self, predicate: Callable[[X], bool]) -> "Xiter[X]":
        return Xiter(filter(predicate, self))

    def foreach(self, statement: Callable[[X], Any]) -> None:
        (statement(e) for e in self)
