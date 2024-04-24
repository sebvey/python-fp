from typing import Callable, Iterable, Iterator, Self

# TODO : add convenience method


class Xiter:

    def __init__(self, iterable: Iterable) -> None:
        if not hasattr(iterable, "__iter__"):
            raise TypeError("Xiter must be constructed from an iterable")
        self.iter: Iterator = iter(iterable)

    def __iter__(self) -> Iterator:
        return self.iter

    def __repr__(self) -> str:
        return repr(self.iter)

    def map(self, f: Callable) -> Self:
        return Xiter(map(f, self))

    def flatMap(self, f: Callable) -> Self:
        return Xiter(el for iterable in self.map(f) for el in iterable)

    def filter(self, predicate: Callable) -> Self:
        return Xiter(filter(predicate, self))

    def foreach(self, statement: Callable) -> None:
        [_ for _ in self.map(statement)]
