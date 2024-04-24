from typing import List, Tuple, Iterable, Iterator, Self, Callable

# from collections import UserList
from copy import deepcopy


class Xlist(Iterable):

    def __init__(self, iterable: Iterable) -> None:

        match iterable:
            case list():
                self.__data = self._convert_list(iterable)
            case tuple():
                self.__data = self._convert_tuple(iterable)
            case object(__iter__=_):
                self.__data = self._convert_iterator(iterable)
            case _:
                raise TypeError(
                    f"Xlist constructed from Iterator, provided : {type(iterable)}"
                )

    @classmethod
    def _convert_list(cls, list: List) -> List:
        return deepcopy(list)

    @classmethod
    def _convert_tuple(cls, tuple: Tuple) -> List:
        return cls._convert_list(list(tuple))

    @classmethod
    def _convert_iterator(cls, iterator: Iterator) -> List:
        return list(iterator)

    def __iter__(self) -> Iterator:
        return iter(self.__data)

    def __eq__(self, other: object) -> bool:
        return self.__data == other.__data

    def map(self, f: Callable) -> Self:
        return Xlist([f(el) for el in self])

    def flatten(self) -> Self:
        return Xlist([inner for outer in self for inner in outer])

    def flatMap(self, f: Callable) -> Self:
        return Xlist([i for el in map(f, self) for i in el])

    def filter(self, predicate: Callable) -> Self:
        return Xlist([el for el in self if predicate(el)])

    def sorted(self, key: None = None, reverse: bool = False) -> Self:
        return Xlist(sorted(self, key=key, reverse=reverse))

    def foreach(self, statement: Callable) -> None:
        self.map(statement)

    def min(self, key: None = None):
        return min(self, key=key)

    def max(self, key: None = None):
        return max(self, key=key)
