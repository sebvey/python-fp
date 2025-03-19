# from _typeshed import SupportsRichComparison # not available ...
from __future__ import annotations
from warnings import warn

from copy import copy, deepcopy
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    Protocol,
    TypeVar,
    cast,
    overload,
)
from collections.abc import Iterable as ABCIterable
from xfp import Xresult, Xtry
from xfp.functions import F1


class _SupportsDunderLT(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...


class _SupportsDunderGT(Protocol):
    def __gt__(self, other: Any, /) -> bool: ...


type _Comparable = _SupportsDunderGT | _SupportsDunderLT

X = TypeVar("X", covariant=True)


def _partially_apply_fold[A, B](
    to_apply_func: F1[[B, F1[[B, A], B]], B], b: B
) -> Callable[[F1[[B, A], B]], B]:
    def applied(f: F1[[B, A], B]) -> B:
        warn(
            "The use of curried version of fold()/fold_left()/fold_right() is deprecated since 1.1.0. "
            "Use corresponding method with both 'zero' and 'f' arguments instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return to_apply_func(b, f)

    return applied


class Xlist(Generic[X]):
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

    def copy(self) -> Xlist[X]:
        "Return a shallow copy of itself."
        return Xlist(copy(self.__data))

    def deepcopy(self) -> Xlist[X]:
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

    def tail(self) -> Xlist[X]:
        """Return the Xlist except its first element.

        ### Raise

        - IndexError -- if the list is empty.
        """
        if len(self) <= 0:
            raise IndexError("<tail> operation not allowed on empty list")
        return Xlist(self.__data[1:])

    def tail_fr(self) -> Xresult[IndexError, Xlist[X]]:
        """Return the Xlist except its first element.

        Wrap the potential error in an Xresult.
        """
        return cast(Xresult[IndexError, Xlist[X]], Xtry.from_unsafe(self.tail))

    def appended[T](self: Xlist[T], el: T) -> Xlist[T]:
        """Return a new Xlist with el appended at its end."""
        newlist = self.copy()
        newlist.__data.append(el)
        return newlist

    def prepended[T](self: Xlist[T], el: T) -> Xlist[T]:
        """Return a new Xlist with el prepended at index 0."""
        newlist = self.copy()
        newlist.__data.insert(0, el)
        return newlist

    def inserted[T](self: Xlist[T], i: int, el: T) -> Xlist[T]:
        """Return a new Xlist with el inserted before position i."""
        newlist = self.copy()
        newlist.__data.insert(i, el)
        return newlist

    def map[T](self, f: F1[[X], T]) -> Xlist[T]:
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

    def filter(self, predicate: F1[[X], bool]) -> Xlist[X]:
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

    def foreach(self, statement: F1[[X], Any]) -> None:
        """Do the 'statement' procedure once for each element of the Xlist.

        ### Usage

        ```python
            from xfp import Xlist

            input = Xlist([1, 2, 3])
            statement = lambda el: print(f"This is an element of the list : {el}")
            input.foreach(statement)
            # This is an element of the list : 1
            # This is an element of the list : 2
            # This is an element of the list : 3
        ```
        """
        [statement(e) for e in self]

    def flatten[XS](self: Xlist[Iterable[XS]]) -> Xlist[XS]:
        """Return a new Xlist with one less level of nest.

        ### Usage

        ```python
            from xfp import Xlist

            assert Xlist([1, 2, 3]).flatten() == Xlist([1, 2, 3])
            assert Xlist([[1, 2], [3]]).flatten() == Xlist([1, 2, 3])
        ```
        """
        return Xlist([el for els in self for el in els])

    def flat_map[T](self, f: F1[[X], Iterable[T]]) -> "Xlist[T]":
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

    @overload
    def min(self: Xlist[_Comparable]) -> X:
        """Return the smallest element of the Xlist. Elements must be comparables.

        ### Raise

        - ValueError -- when the Xlist is empty

        ### Usage

        ```python
            from xfp import Xlist

            input = Xlist(["ae", "bd", "cc"])
            assert input.min() == "ae"
        ```
        """
        ...

    @overload
    def min(self, key: F1[[X], _Comparable]) -> X:
        """Return the smallest element of the Xlist given the key criteria.

        ### Argument

        - key -- the function which extrapolate a sortable from the elements of the list

        ### Raise

        - ValueError -- when the Xlist is empty

        ### Usage

        ```python
            from xfp import Xlist

            input = Xlist(["ae", "bd", "cc"])
            assert input.min(lambda x: x[-1]) == "cc"
        ```
        """
        ...

    def min(self, key: Any = None) -> X:
        return min(self, key=key)

    @overload
    def min_fr(self: Xlist[_Comparable]) -> Xresult[ValueError, X]:
        """Return the smallest element of the Xlist. Elements must be comparables.

        Wrap the potential failure in an Xresult.

        ### Usage

        ```python
            from xfp import Xlist, Xresult, XRBranch

            input = Xlist(["ae", "bd", "cc"])
            assert input.min_fr() == Xresult("ae", XRBranch.RIGHT)
        ```
        """
        ...

    @overload
    def min_fr(self, key: F1[[X], _Comparable]) -> Xresult[ValueError, X]:
        """Return the smallest element of the Xlist given the key criteria.

        Wrap the potential failure in an Xresult.

        ### Argument

        - key -- the function which extrapolate a sortable from the elements of the list

        ### Usage

        ```python
            from xfp import Xlist

            input = Xlist(["ae", "bd", "cc"])
            assert input.min_fr(lambda x: x[-1]) == Xresult("cc", XRBranch.RIGHT)
        ```
        """
        ...

    def min_fr[X](self: Xlist[X], key=None) -> Xresult[ValueError, X]:
        return cast(Xresult[ValueError, X], Xtry.from_unsafe(lambda: self.min(key)))

    @overload
    def max(self: Xlist[_Comparable]) -> X:
        """Return the biggest element of the Xlist. Elements must be comparables.

        ### Raise

        - ValueError -- when the Xlist is empty

        ### Usage

        ```python
            from xfp import Xlist

            input = Xlist(["ae", "bd", "cc"])
            assert input.max() == "cc"
        ```
        """
        ...

    @overload
    def max(self, key: F1[[X], _Comparable]) -> X:
        """Return the biggest element of the Xlist given the key criteria.

        ### Argument

        - key -- the function which extrapolate a sortable from the elements of the list

        ### Raise

        - ValueError -- when the Xlist is empty

        ### Usage

        ```python
            from xfp import Xlist

            input = Xlist(["ae", "bd", "cc"])
            assert input.max(lambda x: x[-1]) == "ae"
        ```
        """
        ...

    def max(self, key: Any = None) -> X:
        return max(self, key=key)

    @overload
    def max_fr(self: Xlist[_Comparable]) -> Xresult[ValueError, X]:
        """Return the biggest element of the Xlist. Elements must be comparables.

        Wrap the potential failure in an Xresult.

        ### Usage

        ```python
            from xfp import Xlist, XResult, XRBranch

            input = Xlist(["ae", "bd", "cc"])
            assert input.max_fr() == Xresult("cc", XRBranch.RIGHT)
        ```
        """
        ...

    @overload
    def max_fr(self, key: F1[[X], _Comparable]) -> Xresult[ValueError, X]:
        """Return the biggest element of the Xlist given the key criteria.

        Wrap the potential failure in an Wresult.

        ### Argument

        - key -- the function which extrapolate a sortable from the elements of the list

        ### Usage

        ```python
            from xfp import Xlist, XResult, XRBranch

            input = Xlist(["ae", "bd", "cc"])
            assert input.max_fr(lambda x: x[-1]) == Xresult("ae", XRBranch.RIGHT)
        ```
        """
        ...

    def max_fr[X](self: Xlist[X], key=None) -> Xresult[ValueError, X]:
        return cast(Xresult[ValueError, X], Xtry.from_unsafe(lambda: self.max(key)))

    @overload
    def sorted(self: Xlist[_Comparable], *, reverse: bool = False) -> Xlist[X]:
        """Return a new Xlist containing the same elements sorted. Elements must be comparables.

        ### Keyword Arguments

        - reverse (default False) -- should we sort ascending (False) or descending (True)

        ### Usage

        ```python
            from xfp import Xlist

            input = Xlist(["bd", "ae", "cc"])
            assert input.sorted() == Xlist(["ae", "bd", "cc"])
            assert input.sorted(reverse=True) == Xlist(["cc", "bd", "ae"])

        ```
        """
        ...

    @overload
    def sorted(self, *, key: F1[[X], _Comparable], reverse: bool = False) -> Xlist[X]:
        """Return a new Xlist containing the same elements sorted given the key criteria.

        ### Keyword Arguments

        - key                     -- the function which extrapolate a sortable from the elements of the list
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

    def sorted(self, key: Any = None, reverse: bool = False) -> Xlist[X]:
        return Xlist(sorted(self, key=key, reverse=reverse))

    def reversed(self) -> Xlist[X]:
        """Return a new Xlist containing the same elements in the reverse order."""
        data: list[X] = self.__data.copy()
        data.reverse()
        return Xlist(data)

    @overload
    def fold_left[Y](self, zero: Y, f: F1[[Y, X], Y]) -> Y:
        """Return the accumulation of the Xlist elements.

        - Uses a custom accumulator (zero, f) to aggregate the elements of the Xlist
        - Initialize the accumulator with the zero value
        - Then from the first to the last element, compute accumulator(n+1) using f, accumulator(n) and self.data[n], such as:
          accumulator(n+1) = f(accumulator(n), self.data[n])
        - Return the last state of the accumulator

        ### Arguments

        - zero -- initial state of the accumulator
        - f    -- accumulation function, compute the next state of the accumulator

        ### Usage

        ```python
            from xfp import Xlist

            assert Xlist([1, 2, 3]).fold_left(0, lambda x, y: x + y) == 6
            assert Xlist([1, 2, 3]).fold_left(10, lambda x, y: x + y) == 16
            assert Xlist(["1", "2", "3"]).fold_left("", lambda x, y: x + y) == "123"
            assert Xlist([]).fold_left(0, lambda x, y: x + y) == 0
        ```
        """
        ...

    @overload
    def fold_left[Y](self, zero: Y) -> F1[[F1[[Y, X], Y]], Y]:
        """@deprecated since 1.1.0 - Use method with both 'zero' and 'f' arguments instead.
        Return the accumulation of the Xlist elements - Curried Version."""
        ...

    def fold_left[Y](
        self, zero: Y, f: F1[[Y, X], Y] | None = None
    ) -> F1[[F1[[Y, X], Y]], Y] | Y:
        def _fold_left(zero: Y, f: F1[[Y, X], Y]) -> Y:
            acc = zero
            for e in self:
                acc = f(acc, e)
            return acc

        if f is None:
            return _partially_apply_fold(_fold_left, zero)
        else:
            return _fold_left(zero, f)

    @overload
    def fold_right[Y](self, zero: Y, f: F1[[Y, X], Y]) -> Y:
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

            assert Xlist([1, 2, 3]).fold_right(0, lambda x, y: x + y) == 6
            assert Xlist([1, 2, 3]).fold_right(10, lambda x, y: x + y) == 16
            assert Xlist(["1", "2", "3"]).fold_right("", lambda x, y: x + y) == "321"
            assert Xlist([]).fold_right(0, lambda x, y: x + y) == 0
        ```
        """
        ...

    @overload
    def fold_right[Y](self, zero: Y) -> F1[[F1[[Y, X], Y]], Y]:
        """@deprecated since 1.1.0 - Use method with both 'zero' and 'f' arguments instead.
        Return the accumulation of the Xlist elements - Curried Version."""
        ...

    def fold_right[Y](
        self, zero: Y, f: F1[[Y, X], Y] | None = None
    ) -> F1[[F1[[Y, X], Y]], Y] | Y:
        def _fold_right(zero: Y, f: F1[[Y, X], Y]) -> Y:
            acc: Y = zero
            for e in self.reversed():
                acc = f(acc, e)
            return acc

        if f is None:
            return _partially_apply_fold(_fold_right, zero)
        else:
            return _fold_right(zero, f)

    @overload
    def fold[Y](self, zero: Y, f: F1[[Y, X], Y]) -> Y:
        """Return the accumulation of the Xlist elements.

        Shorthand for fold_left
        """
        ...

    @overload
    def fold[Y](self, zero: Y) -> F1[[F1[[Y, X], Y]], Y]:
        """@deprecated since 1.1.0 - Use method with both 'zero' and 'f' arguments instead.
        Return the accumulation of the Xlist elements - Curried Version."""
        ...

    def fold[Y](
        self, zero: Y, f: F1[[Y, X], Y] | None = None
    ) -> F1[[F1[[Y, X], Y]], Y] | Y:
        if f is None:
            return self.fold_left(zero)
        else:
            return self.fold_left(zero, f)

    def reduce(self, f: F1[[X, X], X]) -> X:
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

    def reduce_fr(self, f: F1[[X, X], X]) -> Xresult[IndexError, X]:
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

    def zip[T](self, other: Iterable[T]) -> "Xlist[tuple[X, T]]":
        """Zip this Xlist with another iterable."""
        return Xlist(zip(self, other))
