from abc import abstractmethod
from typing import (
    Any,
    Callable,
    Iterator,
    Protocol,
    cast,
    overload,
    runtime_checkable,
)

from xfp import Xlist, Xresult, Xtry, tupled
from .utils import E
from collections.abc import Iterable as ABCIterable


@runtime_checkable
class ABCDict[Y, X](Protocol):
    @abstractmethod
    def items(self) -> ABCIterable[tuple[Y, X]]: ...


class Xdict[Y: E, X: E]:
    @classmethod
    def from_list(cls, iterable: ABCIterable[tuple[Y, X]]) -> "Xdict[Y, X]":
        return cls({k: v for k, v in iterable})

    def __init__(self, dic: ABCDict[Y, X]) -> None:
        self.__data = dict(dic.items())

    def __iter__(self) -> Iterator[tuple[Y, X]]:
        """Return an iterable over the underlying data."""
        return iter(self.items())

    def __len__(self) -> int:
        """Return the length of the underlying data."""
        return len(self.__data)

    def __eq__(self, other: object) -> bool:
        """Return the equality by comparison of inner values (unordered)."""
        match other:
            case ABCDict():
                return set([e for e in self.items()]) == set([e for e in other.items()])
            case _:
                return False

    def __repr__(self) -> str:
        """Return the representation of the underlying data"""
        return f"Xdict({repr(self.__data)})"

    def __getitem__(self, i: Y) -> X:
        """Alias for get(i).

        Exists to enable [] syntax
        """
        return self.get(i)

    @overload
    def get(self, y: Y, /) -> X: ...

    @overload
    def get(self, y: Y, default: E, /) -> X | E: ...

    def get(self, *args) -> X | E:
        match args:
            case [y] if y in self.keys():
                return self.__data.get(y)
            case [y]:
                raise IndexError(f"Key not found in in Xdict : {y}")
            case [y, default]:
                return self.__data.get(y, default)
            case _:
                raise AttributeError("Wrong set of parameter for <get> method")

    def get_fr(self, y: Y, /) -> Xresult[IndexError, X]:
        return cast(Xresult[IndexError, X], Xtry.from_unsafe(lambda: self.get(y)))

    def set_item(self, key: Y, value: E) -> "Xdict[Y, X | E]":
        return self.union(Xdict({key: value}))

    def del_item(self, key: Y) -> "Xdict[Y, X]":
        return self.filter(lambda x, _: x is not key)

    def union(self, other: ABCDict[E, E]) -> "Xdict[Y | E, X | E]":
        return self.from_list(list(self.items()) + list(other.items()))

    def keys(self) -> Xlist[Y]:
        return Xlist(self.__data.keys())

    def values(self) -> Xlist[X]:
        return Xlist(self.__data.values())

    def items(self) -> Xlist[tuple[Y, X]]:
        return Xlist(self.__data.items())

    def map(self, f: Callable[[Y, X], tuple[E, E]]) -> "Xdict[E, E]":
        return self.from_list(self.items().map(tupled(f)))

    def map_keys(self, f: Callable[[Y], E]) -> "Xdict[E, X]":
        return self.map(lambda y, x: (f(y), x))

    def map_values(self, f: Callable[[X], E]) -> "Xdict[Y, E]":
        return self.map(lambda y, x: (y, f(x)))

    def filter(self, predicate: Callable[[Y, X], bool]) -> "Xdict[Y, X]":
        return self.from_list(self.items().filter(tupled(predicate)))

    def filter_keys(self, predicate: Callable[[Y], bool]) -> "Xdict[Y, X]":
        return self.filter(lambda y, _: predicate(y))

    def filter_values(self, predicate: Callable[[X], bool]) -> "Xdict[Y, X]":
        return self.filter(lambda _, x: predicate(x))

    def foreach(self, f: Callable[[Y, X], Any]) -> None:
        self.items().foreach(tupled(f))

    def foreach_keys(self, f: Callable[[Y], Any]) -> None:
        return self.foreach(lambda y, _: f(y))

    def foreach_values(self, f: Callable[[X], Any]) -> None:
        return self.foreach(lambda _, x: f(x))
