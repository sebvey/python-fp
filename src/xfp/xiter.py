from copy import deepcopy
from itertools import tee
import itertools
from typing import Generic, Iterable, Iterator, Any, TypeVar, cast, overload
from collections.abc import Iterable as ABCIterable
from deprecation import deprecated  # type: ignore

from xfp import Xresult, Xlist, Xtry
from xfp.functions import F1, curry2
from xfp.utils import _Comparable

X = TypeVar("X", covariant=True)


class Xiter(Generic[X]):
    """Enhance Lists (lazy) with functional behaviors.

    This class provides common behaviors used for declarative programming.

    ### Features

    - Monadic behavior
    - List proxies or quality of lifes
    - Iter proxy from (itertools homogene)
    """

    @classmethod
    def cycle[T](cls, c: Iterable[T]) -> "Xiter[T]":
        "Proxy for itertools.cycle."
        return Xiter(itertools.cycle(c))

    @classmethod
    def repeat[T](cls, x: T) -> "Xiter[T]":
        "Proxy for itertools.repeat."
        return Xiter(itertools.repeat(x))

    def __init__(self, iterable: Iterable[X]) -> None:
        """Construct an Xiter from an iterable."""
        match iterable:
            case ABCIterable():
                self.__iter: Iterator = iter(iterable)
            case _:
                raise TypeError("Xiter must be constructed from an iterable")

    def __iter__(self) -> Iterator[X]:
        """Return an iterable over the underlying data."""
        return self.__iter

    def __repr__(self) -> str:
        """Return the representation of the underlying data"""
        return repr(self.__iter)

    def __next__(self) -> X:
        """Return the next element of the iterator.

        Consume this element in the data structure.
        """
        return next(self.__iter)

    def __getitem__(self, i: int) -> X:
        """Alias for get(i).

        Exists to enable [] syntax
        """
        return self.get(i)

    def takewhile(self, predicate: F1[[X], bool]) -> "Xiter[X]":
        """Return a new iterator that stops yielding elements when predicate = False.

        Do not consume the original iterator.

        Useful to limit an infinite Xiter with a predicate.

        ### Usage

        ```python
            from xfp import Xiter
            import itertools

            until_xiter = (
                Xiter(itertools.count(start=0,step=2))  # -> Xiter([0,2,4,6,8,...])
                .takewhile(lambda x: x<6)               # -> Xiter([0,2,4])
            )
        ```
        """

        return Xiter(itertools.takewhile(predicate, self.copy().__iter))

    def copy(self) -> "Xiter[X]":
        """Return a new Xiter, tee-ed from self.

        Used to make a shallow copy of the iterator, functional style.

        ## Usage

        ```python
            from xfp import Xiter

            r1 = Xiter(range(10))
            r2 = r1.copy()
            assert next(r1) == 0
            assert next(r2) == 0

        ```
        """
        a, b = tee(self)
        self.__iter = a
        return Xiter(b)

    def deepcopy(self) -> "Xiter[X]":
        """Return a new Xiter, with both iterator and elements distincts from self.

        Used to make a deep copy of the iterator, functional style.

        ## Usage

        ```python
            from xfp import Xiter
            from dataclasses import dataclass

            @dataclass
            class A:
                text: str

            ori = Xiter([A("hello")])
            deep_copy = ori.deepcopy()
            shallow_copy = ori.copy()

            value1 = next(ori)
            value2 = next(deep_copy)
            value3 = next(shallow_copy)

            value1.text = "world"          # 'ori' is mutated
            assert value2.text == "hello"  # 'deep_copy' is left untouched
            assert value3.text == "world"  # on the contrary, 'shallow_copy' still dependents on 'ori'
        ```
        """
        a, b = tee(self)
        self.__iter = Xiter(a)
        return Xiter(map(deepcopy, b))

    def chain[T](self, other: Iterable[T]) -> "Xiter[X | T]":
        """Proxy for itertools.chain.

        Return a chain object whose `.__next__()` method returns elements from the
        first iterable until it is exhausted, then elements from the next
        iterable, until all of the iterables are exhausted.
        """
        return Xiter(itertools.chain(self, other))

    def get(self, i: int) -> X:
        """Return the i-th element of the Xiter.

        Does not consume the i-1 first elements, but evaluate them.

        ### Raise

        - IndexError -- if the Xiter is shorter than i
        """
        __copy = self.copy()

        try:
            for _ in range(i):
                next(__copy)
            return next(__copy)
        except StopIteration:
            raise IndexError(f"Xiter has less than {i} element(s)")

    def get_fr(self, i: int) -> Xresult[IndexError, X]:
        """Return the i-th element of the Xiter.

        Does not consume the i-1 first elements, but evaluate them.
        Wrap the potential error in an Xresult.
        """
        return cast(Xresult[IndexError, X], Xtry.from_unsafe(lambda: self.get(i)))

    @deprecated("1.1.0", "2.0.0", details="Use get_fr instead")
    def get_fx(self, i: int) -> Xresult[IndexError, X]:
        """Return the i-th element of the Xiter.

        Does not consume the i-1 first elements, but evaluate them.
        Wrap the potential error in an Xresult.
        """
        return self.get_fr(i)

    def head(self) -> X:
        """Alias for get(0)."""
        return self.get(0)

    def head_fr(self) -> Xresult[IndexError, X]:
        """Alias for get_fr(0)."""
        return self.get_fr(0)

    @deprecated("1.1.0", "2.0.0", details="Use head_fr instead")
    def head_fx(self) -> Xresult[IndexError, X]:
        """Alias for get_fx(0)."""
        return self.head_fr()

    def tail(self) -> "Xiter[X]":
        """Return the iterator / its first element.

        ### Raise

        - IndexError -- if the list is empty.
        """
        try:
            out = self.copy()
            next(out)
            return out
        except StopIteration:
            raise IndexError("<tail> operation not allowed on empty iterator")

    def tail_fr(self) -> Xresult[IndexError, "Xiter[X]"]:
        """Return the iterator / its first element.

        Wrap the potential error in an Xresult.
        """
        return cast(Xresult[IndexError, "Xiter[X]"], Xtry.from_unsafe(self.tail))

    @deprecated("1.1.0", "2.0.0", details="Use tail_fr instead")
    def tail_fx(self) -> Xresult[IndexError, "Xiter[X]"]:
        """Return the iterator / its first element.

        Wrap the potential error in an Xresult.
        """
        return self.tail_fr()

    def appended[T](self: "Xiter[T]", el: T) -> "Xiter[T]":
        """Return a new iterator with el appended.

        After exhaustion of self, the next `next` call will return `el`.
        """
        return self.chain([el])

    def prepended[T](self: "Xiter[T]", el: T) -> "Xiter[T]":
        """Return a new iterator with el prepended.

        Before iterating over self, the first `next` call will return `el`.
        """
        return Xiter([el]).chain(self)

    def map[T](self, f: F1[[X], T]) -> "Xiter[T]":
        """Return a new iterator, with f applied to each future element.

        ### Usage

        ```python
            from xfp import Xiter

            input = Xiter([1, 2, 3])
            assert next(input) == 1
            f = lambda el: el*el
            result = input.map(f)
            assert next(result) == 4 # Xiter([2*2, 3*3]) => 2*2 == 4
        ```
        """
        return Xiter(map(f, self.copy()))

    def filter(self, predicate: F1[[X], bool]) -> "Xiter[X]":
        """Return a new iterator skipping the elements with predicate = False.

        ### Usage

        ```python
            from xfp import Xiter

            input = Xiter(range(1,5))
            predicate = lambda el: el % 2 == 0
            r1 = input.filter(predicate)
            # keep only even numbers
            assert next(r1) == 2
            assert next(r1) == 4
        ```
        """
        return Xiter(filter(predicate, self.copy()))

    def foreach(self, statement: F1[[X], Any]) -> None:
        """Do the 'statement' procedure once for each element of the iterator.

        Do not consume the original iterator.

        ### Usage

        ```python
            from xfp import Xiter

            input = Xiter(range(1,4))
            statement = lambda el: print(f"This is an element of the range : ${el}")
            input.foreach(statement)
            # This is an element of the range : 1
            # This is an element of the range : 2
            # This is an element of the range : 3

            input.foreach(statement) # you can reconsume the same iterable
            # This is an element of the range : 1
            # This is an element of the range : 2
            # This is an element of the range : 3

        ```
        """
        [statement(e) for e in self.copy()]

    def flatten[XS](self: "Xiter[Iterable[XS]]") -> "Xiter[XS]":
        """Return a new iterator, with each element nested iterated on individually.

        ## Usage

        ```python
            from xfp import Xiter

            # All the following resulting objects are equivalent to Xiter([1,2,3])
            Xiter([1, 2, 3]).flatten()
            Xiter([[1, 2], [3]]).flatten()
            Xiter([[1, 2], 3]).flatten()
        ```
        """

        def result(xi):
            for el in xi:
                for inner_el in el:
                    yield inner_el

        return Xiter(result(self.copy()))

    def flat_map[T](self, f: F1[[X], Iterable[T]]) -> "Xiter[T]":
        """Return the result of map and then flatten.

        Exists as homogenisation with Xresult.flat_map.

        ### Usage

        ```python
            from xfp import Xiter, Xlist

            Xiter([1, 2, 3]).flat_map(lambda x: Xlist([(x, 4), (x, 5)]))
            # equivalent to Xiter([(1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5)])
        ```
        """
        return self.map(f).flatten()

    def fold_left[T](self, zero: T, f: F1[[T, X], T]) -> T:
        """Return the accumulation of the Xiter elements.

        - Uses a custom accumulator (zero, f) to aggregate the elements of the Xiter
        - Initialize the accumulator with the zero value
        - Then from the first to the last element, compute accumulator(n+1) using f, accumulator(n) and self.data[n], such as:
          accumulator(n+1) = f(accumulator(n), self.data[n])
        - Return the last state of the accumulator

        ### Keyword Arguments

        - zero -- initial state of the accumulator
        - f    -- accumulation function, compute the next state of the accumulator

        ### Warnings

        This function falls in infinite loop in the case of infinite iterator.

        ### Usage

        ```python
            from xfp import Xiter

            assert Xiter([1, 2, 3]).fold_left(0)(lambda x, y: x + y) == 6
            assert Xiter([1, 2, 3]).fold_left(10)(lambda x, y: x + y) == 16
            assert Xiter(["1", "2", "3"]).fold_left("")(lambda x, y: x + y) == "123"
            assert Xiter([]).fold_left(0)(lambda x, y: x + y) == 0
        ```
        """
        acc: T = zero
        for e in self:
            acc = f(acc, e)
        return acc

    def fold[T](self, zero: T, f: F1[[T, X], T]) -> T:
        """Return the accumulation of the Xiter elements.

        Shorthand for fold_left
        """
        return self.fold_left(zero, f)

    def reduce(self, f: F1[[X, X], X]) -> X:
        """Return the accumulation of the Xiter elements using the first element as the initial state of accumulation.

        ### Raise

        - IndexError -- when the Xiter is empty

        ### Keyword Arguments

        - f -- accumulation function, compute the next state of the accumulator

        ### Warning

        This function falls in infinite loop in the case of infinite iterator.

        ### Usage

        ```python
            from xfp import Xiter
            import pytest

            assert Xiter([1, 2, 3]).reduce(lambda x, y: x + y) == 6
            assert Xiter(["1", "2", "3"]).reduce(lambda x, y: x + y) == "123"
            with pytest.raises(IndexError):
                Xiter([]).reduce(lambda x, y: x + y)
        ```
        """
        try:
            h = self.head()
        except IndexError:
            raise IndexError("<reduce> operation not allowed on empty list")
        return self.tail().fold(h, f)

    def reduce_fr(self, f: F1[[X, X], X]) -> Xresult[IndexError, X]:
        """Return the accumulation of the Xiter elements using the first element as the initial state of accumulation.

        Wrap the potential error in an Xresult.

        ### Keyword Arguments

        - f -- accumulation function, compute the next state of the accumulator

        ### Warning

        This function falls in infinite loop in the case of infinite iterator.

        ### Usage

        ```python
            from xfp import Xiter, Xtry

            Xiter([1, 2, 3]).reduce_fr(lambda x, y: x + y)       # -> Xtry.Success(6)
            Xiter(["1", "2", "3"]).reduce_fr(lambda x, y: x + y) # -> Xtry.Success("123")
            Xiter([]).reduce_fr(lambda x, y: x + y)              # -> Xtry.Failure(IndexError("<reduce> operation not allowed on empty list"))

        ```
        """
        return cast(Xresult[IndexError, X], Xtry.from_unsafe(lambda: self.reduce(f)))

    def min(self, key: F1[[X], _Comparable] = id) -> X:
        """Return the smallest element of the Xiter given the key criteria.

        ### Raise

        - ValueError -- when the Xiter is empty

        ### Keyword Arguments

        - key (default id) -- the function which extrapolate a sortable from the elements of the list

        ### Warning

        This function falls in infinite loop in the case of infinite iterator.

        ### Usage

        ```python
            from xfp import Xiter
            import pytest

            input = Xiter(["ae", "bd", "cc"])
            assert input.min() == "ae"
            assert input.min(lambda x: x[-1]) == "cc"
            with pytest.raises(IndexError):
                Xiter([]).min()
        ```
        """
        return min(self, key=key)

    def min_fr(self, key: F1[[X], _Comparable] = id) -> Xresult[ValueError, X]:
        """Return the smallest element of the Xiter given the key criteria.

        Wrap the potential failure in an Wresult

        ### Warning

        This function falls in infinite loop in the case of infinite iterator.
        ```
        """
        return cast(Xresult[ValueError, X], Xtry.from_unsafe(lambda: self.min(key)))

    def max(self, key: F1[[X], _Comparable] = id) -> X:
        """Return the bigget element of the Xiter given the key criteria.

        ### Raise

        - ValueError -- when the Xiter is empty

        ### Keyword Arguments

        - key (default id) -- the function which extrapolate a sortable from the elements of the list

        ### Warning

        This function falls in infinite loop in the case of infinite iterator.

        ### Usage

        ```python
            from xfp import Xiter
            import pytest

            input = Xiter(["ae", "bd", "cc"])
            assert input.max() == "cc"
            assert input.max(lambda x: x[-1]) == "ae"
            with pytest.raises(IndexError):
                Xiter([]).max()
        ```
        """
        return max(self, key=key)

    def max_fr(self, key: F1[[X], _Comparable] = id) -> Xresult[ValueError, X]:
        """Return the biggest element of the Xiter given the key criteria.

        Wrap the potential failure in an Wresult

        ### Warning

        This function falls in infinite loop in the case of infinite iterator.
        ```
        """
        return cast(Xresult[ValueError, X], Xtry.from_unsafe(lambda: self.max(key)))

    def take(self, n: int) -> "Xiter[X]":
        """Return a new iterator limited to the first 'n' elements.
        Return a copy if the original iterator has less than 'n' elements.
        Return an empty Xiter if n is negative.

        Do not consume the original iterator.

        ### Usage

        ```python
                from xfp import Xiter
                import itertools

                infinite_xiter = Xiter(itertools.repeat(42))  # -> Xiter([42,42,42,...])
                until_xiter = infinite_xiter.take(3)          # -> Xiter([42,42])
            ```
        """

        return Xiter(self.slice(n))

    def takeuntil(self, predicate: F1[[X], bool]) -> "Xiter[X]":
        """Return a new iterator that stops yielding elements when predicate = True.

        Do not consume the original iterator.

        Useful to limit an infinite Xiter with a predicate.

        ### Usage

        ```python
            from xfp import Xiter
            import itertools

            infinite_xiter = Xiter(itertools.count(start=0,step=2))  # -> Xiter([0,2,4,6,8,...])
            until_xiter = infinite_xiter.takeuntil(lambda x: x >=6)  # -> Xiter([0,2,4])
        ```
        """

        # fixes "error: Cannot use a covariant type variable as a parameter" on lambda x: not predicate(x)
        @curry2
        def invert[T](p: F1[[T], bool], x: T) -> bool:
            return not p(x)

        return self.takewhile(invert(predicate))

    @overload
    def slice(self, stop: int | None, /) -> "Xiter[X]": ...

    @overload
    def slice(
        self, start: int | None, stop: int | None, step: int | None = 1, /
    ) -> "Xiter[X]": ...

    def slice(self, *args) -> "Xiter[X]":
        """Return an new Xiter with selected elements from the Xiter.
        Works like sequence slicing but does not support negative values
        for start, stop, or step.

        Do not consume the original iterator.

        If start is zero or None, iteration starts at zero.
        Otherwise, elements from the iterable are skipped until start is reached.

        If stop is None, iteration continues until the input is exhausted,
        if at all. Otherwise, it stops at the specified position.

        If step is None, the step defaults to one.
        Elements are returned consecutively unless step is set higher than
        one which results in items being skipped.
        """
        __iter_copy = self.copy()

        if len(args) not in (1, 2, 3):
            raise TypeError(
                "slice expected from 1 to 3 positional arguments: 'stop' | 'start' 'stop' ['step']"
            )

        return Xiter(itertools.islice(__iter_copy, *args))

    def zip[T](self, other: Iterable[T]) -> "Xiter[tuple[X, T]]":
        """Zip this iterator with another iterable."""
        return Xiter(zip(self.copy(), other))

    def to_Xlist(self) -> "Xlist[X]":
        """Return an Xlist being the evaluated version of self.

        Do not consume the original iterator.
        """
        return Xlist(self.copy())
