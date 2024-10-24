from copy import deepcopy
from itertools import tee
import itertools
from typing import Callable, Iterable, Iterator, Any, cast
from collections.abc import Iterable as ABCIterable

from xfp import Xresult, Xlist, Xtry
from .utils import E


class Xiter[X: E]:
    """Enhance Lists (lazy) with functional behaviors.

    This class provides common behaviors used for declarative programming.

    ### Features

    - Monadic behavior
    - List proxies or quality of lifes
    - Iter proxy from (itertools homogene)
    """

    @classmethod
    def cycle(cls, c: Iterable[X]) -> "Xiter[X]":
        "Proxy for itertools.cycle."
        return Xiter(itertools.cycle(c))

    @classmethod
    def repeat(cls, x: X) -> "Xiter[X]":
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

    def copy(self):
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

    def deepcopy(self):
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
        return Xiter(b).map(lambda x: deepcopy(x))

    def chain(self, other: Iterable[X]) -> "Xiter[X]":
        """Proxy for itertools.chain.

        Return a chain object whose `.__next__()` method returns elements from the
        first iterable until it is exhausted, then elements from the next
        iterable, until all of the iterables are exhausted.
        """
        return Xiter(itertools.chain(self, other))

    def get(self, i: int) -> X:
        """Return the i-th element of the Xlist.

        Does not consume the i-1 first elements, but evaluate them.

        ### Raise

        - IndexError -- if the list is shorter than i
        """
        if i == 0:
            try:
                return next(self.copy())
            except StopIteration:
                raise IndexError("<next> operation not allowed on empty iterator")
        else:
            return self.tail().get(i - 1)

    def get_fx(self, i: int) -> Xresult[IndexError, X]:
        """Return the i-th element of the Xlist.

        Does not consume the i-1 first elements, but evaluate them.
        Wrap the potential error in an Xresult.
        """
        return cast(Xresult[IndexError, X], Xtry.from_unsafe(lambda: self.get(i)))

    def head(self) -> X:
        """Alias for get(0)."""
        return self.get(0)

    def head_fx(self) -> Xresult[IndexError, X]:
        """Alias for get_fx(0)."""
        return self.get_fx(0)

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

    def tail_fx(self) -> Xresult[IndexError, "Xiter[X]"]:
        """Return the iterator / its first element.

        Wrap the potential error in an Xresult.
        """
        return cast(Xresult[IndexError, "Xiter[X]"], Xtry.from_unsafe(self.tail))

    def map(self, f: Callable[[X], E]) -> "Xiter[E]":
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

    def filter(self, predicate: Callable[[X], bool]) -> "Xiter[X]":
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

    def foreach(self, statement: Callable[[X], Any]) -> None:
        """Do the 'statement' procedure once for each element of the iterator.

        Do not consume the original iterator

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

    def flatten(self) -> "Xiter[E]":
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
                if isinstance(el, ABCIterable):
                    for inner_el in el:
                        yield inner_el
                else:
                    yield el

        return Xiter(result(self.copy()))

    def flat_map(self, f: Callable[[X], Iterable[E]]) -> "Xiter[E]":
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

    def zip(self, other: Iterable[E]) -> "Xiter[tuple[X, E]]":
        """Zip this iterator with another iterable."""
        return Xiter(zip(self.copy(), other))

    def to_Xlist(self) -> "Xlist[X]":
        """Return an Xlist being the evaluated version of self."""
        return Xlist(self)
