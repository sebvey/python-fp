from copy import deepcopy
from itertools import tee
import itertools
from typing import Callable, Iterable, Iterator, Any, cast
from collections.abc import Iterable as ABCIterable

from xfp import Xeffect, Xlist
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
            r1 = Xiter([1, 2, 3])
            r2 = r1.copy()
            assert next(r1) == 1
            assert next(r2) == 1
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
            @dataclass
            class A:
                text: str

            r1 = Xiter([A("hello")])
            r2 = r1.deepcopy()
            value1 = next(r1)
            value2 = next(r2)

            value1.text = "world"
            assert value2.text == "hello"
        ```
        """
        a, b = tee(self)
        self.__iter = Xiter(a).map(lambda x: deepcopy(x))
        return Xiter(b)

    def chain(self, other: Iterable[X]) -> "Xiter[X]":
        """Proxy for itertools.chain."""
        return Xiter(itertools.chain(self, other))

    def get(self, i: int) -> X:
        """Return the i-th element of the Xlist.

        Does not consume the i-1 first elements, but evaluate them

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

    def get_fx(self, i: int) -> Xeffect[IndexError, X]:
        """Return the i-th element of the Xlist.

        Does not consume the i-1 first elements, but evaluate them
        Wrap the potential error in an effect
        """
        return cast(Xeffect[IndexError, X], Xeffect.from_unsafe(lambda: self.get(i)))

    def head(self) -> X:
        """Alias for get(0)."""
        return self.get(0)

    def head_fx(self) -> Xeffect[IndexError, X]:
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

    def tail_fx(self) -> Xeffect[IndexError, "Xiter[X]"]:
        """Return the iterator / its first element.

        Wrap the potential error in an effect.
        """
        return cast(Xeffect[IndexError, "Xiter[X]"], Xeffect.from_unsafe(self.tail))

    def map(self, f: Callable[[X], E]) -> "Xiter[E]":
        """Return a new iterator, with f applied to each future element.

        ### Usage

        ```python
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
            input = Xiter([1, 2, 3, 4])
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
            input = Xiter([1, 2, 3])
            statement = lambda el: println(f"This is an element of the list : ${el}")
            input.foreach(statement)
            # This is an element of the list : 1
            # This is an element of the list : 2
            # This is an element of the list : 3

            input.foreach(statement) # you can reconsume the same iterator
            # This is an element of the list : 1
            # This is an element of the list : 2
            # This is an element of the list : 3
        ```
        """
        [statement(e) for e in self.copy()]

    def flatten(self) -> "Xiter[E]":
        """Return a new iterator, with each element nested iterated on individually.

        ## Usage

        ```python
            # Xiter([1, 2, 3])
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

        Exists as homogenisation with Xeffect.flat_map.

        ### Usage

        ```python
            Xiter([1, 2, 3]).flat_map(lambda x: Xlist([(x, 4), (x, 5)]))
            # Xiter([(1, 4), (2, 4), (3, 4), (1, 5), (2, 5), (3, 5)])
        ```
        """
        return self.map(f).flatten()

    def zip(self, other: Iterable[E]) -> "Xiter[tuple[X, E]]":
        """Zip this iterator with another iterable."""
        return Xiter(zip(self.copy(), other))

    def to_Xlist(self) -> "Xlist[X]":
        """Return an Xlist being the evaluated version of self."""
        return Xlist(self)
