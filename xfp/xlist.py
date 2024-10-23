# from _typeshed import SupportsRichComparison # not available ...

from copy import copy, deepcopy
from typing import Iterable, Iterator, Callable, Any, cast
from collections.abc import Iterable as ABCIterable

from xfp import Xresult, Xtry
from .utils import E, curry_method, id


class Xlist[X: E]:
    """Enhance Lists (eager) with functional behaviors.

    This class provides common behaviors used for declarative programming.

    ### Features

    - Monadic behavior
    - Descriptive accumulation
    - List proxies or quality of lifes
    """

    def __init__(self, iterable: Iterable[X]) -> None:
        """Construct an Xlist from an iterable."""
        match iterable:
            case ABCIterable():
                self.__data = list(iterable)
            case _:
                raise TypeError(
                    f"'{type(iterable).__name__}' not allowed for Xlist constructor"
                )

    def __iter__(self) -> Iterator[X]:
        """Return an iterable over the underlying data."""
        return iter(self.__data)

    def __eq__(self, other: object) -> bool:
        """Return the equality by comparison of inner values (and order)."""
        match other:
            case ABCIterable():
                return [e for e in self] == [e for e in other]
            case _:
                return False

    def __len__(self) -> int:
        """Return the length of the underlying data."""
        return len(self.__data)

    def __repr__(self) -> str:
        """Return the representation of the underlying data"""
        return f"Xlist({repr(self.__data)})"

    def __getitem__(self, i: int) -> X:
        """Alias for get(i).

        Exists to enable [] syntax
        """
        return self.get(i)

    def copy(self) -> "Xlist[X]":
        "Return a shallow copy of itself."
        return Xlist(copy(self.__data))

    def deepcopy(self) -> "Xlist[X]":
        "Return a deep copy of itself."
        return Xlist(deepcopy(self.__data))

    def get(self, i: int) -> X:
        """Return the i-th element of the Xlist.

        ### Raise

        - IndexError -- if the list is shorter than i
        """
        if len(self) <= i:
            raise IndexError(
                f"<get> operation not allowed on list shorter than index {i} (found {len(self)} elements)."
            )
        return self.__data[i]

    def get_fr(self, i: int) -> Xresult[IndexError, X]:
        """Return the i-th element of the Xlist.

        Wrap the potential error in an Xresult.
        """
        return cast(Xresult[IndexError, X], Xtry.from_unsafe(lambda: self.get(i)))

    def head(self) -> X:
        """Alias for get(0)."""
        return self.get(0)

    def head_fr(self) -> Xresult[IndexError, X]:
        """Alias for get_fr(0)."""
        return self.get_fr(0)

    def tail(self) -> "Xlist[X]":
        """Return the Xlist except its first element.

        ### Raise

        - IndexError -- if the list is empty.
        """
        if len(self) <= 0:
            raise IndexError("<tail> operation not allowed on empty list")
        return Xlist(self.__data[1:])

    def tail_fr(self) -> Xresult[IndexError, "Xlist[X]"]:
        """Return the Xlist except its first element.

        Wrap the potential error in an Xresult.
        """
        return cast(Xresult[IndexError, "Xlist[X]"], Xtry.from_unsafe(self.tail))

    def map(self, f: Callable[[X], E]) -> "Xlist[E]":
        """Return a new Xlist with the function f applied to each element.

        ### Usage

        ```python
            from xfp import Xlist

            input = Xlist([1, 2, 3])
            f = lambda el: el*el
            assert input.map(f) == Xlist([f(1), f(2), f(3)]) # == Xlist([1, 4, 9])
        ```
        """
        return Xlist([f(el) for el in self])

    def filter(self, predicate: Callable[[X], bool]) -> "Xlist[X]":
        """Return a new Xlist containing only the elements for which predicate is True.

        ### Usage

        ```python
            from xfp import Xlist

            input = Xlist([1, 2, 3, 4])
            predicate = lambda el: el % 2 == 0
            assert input.filter(predicate) == Xlist([2, 4]) # keep only even numbers
        ```
        """
        return Xlist([el for el in self if predicate(el)])

    def foreach(self, statement: Callable[[X], Any]) -> None:
        """Do the 'statement' procedure once for each element of the Xlist.

        ### Usage

        ```python
            from xfp import Xlist

            input = Xlist([1, 2, 3])
            statement = lambda el: print(f"This is an element of the list : ${el}")
            input.foreach(statement)
            # This is an element of the list : 1
            # This is an element of the list : 2
            # This is an element of the list : 3
        ```
        """
        [statement(e) for e in self]

    def flatten(self) -> "Xlist[E]":
        """Return a new Xlist with one less level of nest.

        ### Usage

        ```python
            from xfp import Xlist

            assert Xlist([1, 2, 3]).flatten() == Xlist([1, 2, 3])
            assert Xlist([[1, 2], [3]]).flatten() == Xlist([1, 2, 3])
            assert Xlist([[1, 2], 3]).flatten() == Xlist([1, 2, 3])
        ```
        """
        flatten_data = list()
        for el in self:
            if isinstance(el, ABCIterable):
                for inner_el in el:
                    flatten_data.append(inner_el)
            else:
                flatten_data.append(el)

        return Xlist(flatten_data)

    def flat_map(self, f: Callable[[X], Iterable[E]]) -> "Xlist[E]":
        """Return the result of map and then flatten.

        Exists as homogenisation with Xresult.flat_map

        ### Usage

        ```python
            from xfp import Xlist

            actual   = Xlist([1, 2, 3]).flat_map(lambda x: Xlist([x, 5]))
            expected = Xlist([1, 5, 2, 5, 3, 5])
            assert actual == expected
        ```
        """
        return self.map(f).flatten()

    def min(self, key: Callable[[X], E] = id) -> X:
        """Return the smallest element of the Xlist given the key criteria.

        ### Keyword Arguments

        - key (default id) -- the function which extrapolate a sortable from the elements of the list

        ### Usage

        ```python
            from xfp import Xlist

            input = Xlist(["ae", "bd", "cc"])
            assert input.min() == "ae"
            assert input.min(lambda x: x[-1]) == "cc"
        ```
        """
        return min(self, key=key)

    def max(self, key: Callable[[X], E] = id) -> X:
        """Return the biggest element of the Xlist given the key criteria.

        ### Keyword Arguments

        - key (default id) -- the function which extrapolate a sortable from the elements of the list

        ### Usage

        ```python
            from xfp import Xlist

            input = Xlist(["ae", "bd", "cc"])
            assert input.max() == "cc"
            assert input.max(lambda x: x[-1]) == "ae"
        ```
        """
        return max(self, key=key)

    def sorted(self, key: Callable[[X], E] = id, reverse: bool = False) -> "Xlist[X]":
        """Return a new Xlist containing the same elements sorted given the key criteria.

        ### Keyword Arguments

        - key (default id)        -- the function which extrapolate a sortable from the elements of the list
        - reverse (default False) -- should we sort ascending (False) or descending (True)

        ### Usage

        ```python
            from xfp import Xlist

            input = Xlist(["bd", "ae", "cc"])
            assert input.sorted() == Xlist(["ae", "bd", "cc"])
            assert input.sorted(lambda x: x[-1]) == Xlist(["cc", "bd", "ae"])
            assert input.sorted(lambda x: x[-1], reverse = True) == Xlist(["ae", "bd", "cc"])
        ```
        """
        return Xlist(sorted(self, key=key, reverse=reverse))

    def reversed(self) -> "Xlist[X]":
        """Return a new Xlist containing the same elements in the reverse order."""
        data: list[X] = self.__data.copy()
        data.reverse()
        return Xlist(data)

    @curry_method
    def fold_left(self, zero: E, f: Callable[[E, X], E]) -> E:
        """Return the accumulation of the Xlist elements.

        - Uses a custom accumulator (zero, f) to aggregate the elements of the Xlist
        - Initialize the accumulator with the zero value
        - Then from the first to the last element, compute accumulator(n+1) using f, accumulator(n) and self.data[n], such as:
          accumulator(n+1) = f(accumulator(n), self.data[n])
        - Return the last state of the accumulator

        ### Keyword Arguments

        - zero -- initial state of the accumulator
        - f    -- accumulation function, compute the next state of the accumulator

        ### Usage

        ```python
            from xfp import Xlist

            assert Xlist([1, 2, 3]).fold_left(0)(lambda x, y: x + y) == 6
            assert Xlist([1, 2, 3]).fold_left(10)(lambda x, y: x + y) == 16
            assert Xlist(["1", "2", "3"]).fold_left("")(lambda x, y: x + y) == "123"
            assert Xlist([]).fold_left(0)(lambda x, y: x + y) == 0
        ```
        """
        acc: E = zero
        for e in self:
            acc = f(acc, e)
        return acc

    @curry_method
    def fold_right(self, zero: E, f: Callable[[X, E], E]) -> E:
        """Return the accumulation of the Xlist elements.

        - Uses a custom accumulator (zero, f) to aggregate the elements of the Xlist
        - Initialize the accumulator with the zero value
        - Then from the last to the first element, compute accumulator(n+1) using f, accumulator(n) and self.data[n], such as:
          accumulator(n+1) = f(accumulator(n), self.data[n])
        - Return the last state of the accumulator

        ### Keyword Arguments

        - zero -- initial state of the accumulator
        - f    -- accumulation function, compute the next state of the accumulator

        ### Usage

        ```python
            from xfp import Xlist

            assert Xlist([1, 2, 3]).fold_right(0)(lambda x, y: x + y) == 6
            assert Xlist([1, 2, 3]).fold_right(10)(lambda x, y: x + y) == 16
            assert Xlist(["1", "2", "3"]).fold_right("")(lambda x, y: x + y) == "321"
            assert Xlist([]).fold_right(0)(lambda x, y: x + y) == 0
        ```
        """
        return self.reversed().fold_left(zero)(lambda e, t: f(e, t))

    @curry_method
    def fold(self, zero: X, f: Callable[[E, X], E]) -> E:
        """Return the accumulation of the Xlist elements.

        Shorthand for fold_left
        """
        return self.fold_left(zero)(f)

    def reduce(self, f: Callable[[X, X], X]) -> X:
        """Return the accumulation of the Xlist elements using the first element as the initial state of accumulation.

        ### Raise

        - IndexError -- when the Xlist is empty

        ### Keyword Arguments

        - f -- accumulation function, compute the next state of the accumulator

        ### Usage

        ```python
            from xfp import Xlist
            import pytest

            assert Xlist([1, 2, 3]).reduce(lambda x, y: x + y) == 6
            assert Xlist(["1", "2", "3"]).reduce(lambda x, y: x + y) == "123"
            with pytest.raises(IndexError):
                Xlist([]).reduce(lambda x, y: x + y)
        ```
        """
        if len(self) <= 0:
            raise IndexError("<reduce> operation not allowed on empty list")
        return self.tail().fold(self.head())(f)

    def reduce_fr(self, f: Callable[[X, X], X]) -> Xresult[IndexError, X]:
        """Return the accumulation of the Xlist elements using the first element as the initial state of accumulation.

        Wrap the potential error in an Xresult.

        ### Keyword Arguments

        - f -- accumulation function, compute the next state of the accumulator

        ### Usage

        ```python
            from xfp import Xlist, Xtry

            Xlist([1, 2, 3]).reduce_fr(lambda x, y: x + y)       # -> Xtry.Success(6)
            Xlist(["1", "2", "3"]).reduce_fr(lambda x, y: x + y) # -> Xtry.Success("123")
            Xlist([]).reduce_fr(lambda x, y: x + y)              # -> Xtry.Failure(IndexError("<reduce> operation not allowed on empty list"))

        ```
        """
        return cast(Xresult[IndexError, X], Xtry.from_unsafe(lambda: self.reduce(f)))

    def zip(self, other: Iterable[E]) -> "Xlist[tuple[X, E]]":
        """Zip this Xlist with another iterable."""
        return Xlist(zip(self, other))
