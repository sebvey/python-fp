# from _typeshed import SupportsRichComparison # not available ...

from typing import Iterable, Iterator, Callable, Any
from collections.abc import Iterable as ABCIterable
from .utils import E, id


class Xlist[X: E]:
    """Enhance Lists (eager) with functional behaviors.

    This class provides common behaviors used for declarative programming.
    It brings :
    Monadic behavior through :
    - map
    - flat_map
    - flatten
    - filter
    - foreach
    Descriptive accumulation through :
    - min |- and sorted/reverse by extension
    - max |
    - fold
    - fold_left
    - fold_right
    - reduce
    List proxies or quality of lifes :
    - head
    - tail
    - iter
    - len
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

    def head(self) -> X:
        """Return the first element of the Xlist.

        Raise:
        IndexError -- if the list is empty.
        """
        if len(self) <= 0:
            raise IndexError("<head> operation not allowed on empty list")
        return self.__data[0]

    def tail(self) -> "Xlist[X]":
        """Return the Xlist / its first element.

        Raise:
        IndexError -- if the list is empty.
        """
        if len(self) <= 0:
            raise IndexError("<tail> operation not allowed on empty list")
        return Xlist(self.__data[1:])

    def map(self, f: Callable[[X], E]) -> "Xlist[E]":
        """Return a new Xlist with the function f applied to each element.

        Keyword arguments:
        f -- the transformation to apply to each element of the list
        Usage:
        input = Xlist([1, 2, 3])
        f = lambda el: el*el
        assert input.map(f) == Xlist([f(1), f(2), f(3)]) # == Xlist([1, 4, 9])
        """
        return Xlist([f(el) for el in self])

    def filter(self, predicate: Callable[[X], bool]) -> "Xlist[X]":
        """Return a new Xlist containing only the elements for which predicate is True.

        Keyword arguments:
        predicate -- the function describing which elements to keep
        Usage:
        input = Xlist([1, 2, 3, 4])
        predicate = lambda el: el % 2 == 0
        assert input.filter(predicate) == Xlist([2, 4]) # keep only even numbers
        """
        return Xlist([el for el in self if predicate(el)])

    def foreach(self, statement: Callable[[X], Any]) -> None:
        """Do the 'statement' procedure once for each element of the Xlist.

        Keyword arguments:
        statement -- the procedure to execute for each element
        Usage:
        input = Xlist([1, 2, 3])
        statement = lambda el: println(f"This is an element of the list : ${el}")
        input.foreach(statement)
        # This is an element of the list : 1
        # This is an element of the list : 2
        # This is an element of the list : 3
        """
        return Xlist([f(el) for el in self])

    def filter(self, predicate: Callable[[X], bool]) -> "Xlist[X]":
        return Xlist([el for el in self if predicate(el)])

    def foreach(self, statement: Callable[[X], Any]) -> None:
        (statement(e) for e in self)

    # TODO : Document
    def flatten(self) -> "Xlist[E]":
        return Xlist([inner for e in self if isinstance(e, ABCIterable) for inner in e])

    def flat_map(self, f: Callable[[X], Iterable[E]]) -> "Xlist[E]":
        return self.map(f).flatten()

    def min(self, key: Callable[[X], E] = id) -> X:
        return min(self, key=key)

    def max(self, key: Callable[[X], E] = id) -> X:
        return max(self, key=key)

    def sorted(self, key: Callable[[X], E] = id, reverse: bool = False) -> "Xlist[X]":
        return Xlist(sorted(self, key=key, reverse=reverse))

    def reverse(self) -> "Xlist[X]":
        data: list[X] = self.__data.copy()
        data.reverse()
        return Xlist(data)

    def fold_left(self, zero: E) -> Callable[[Callable[[E, X], E]], E]:
        def inner(f: Callable[[E, X], E]) -> E:
            acc: E = zero
            for e in self:
                acc = f(acc, e)
            return acc

        return inner

    def fold_right(self, zero: E) -> Callable[[Callable[[X, E], E]], E]:
        def inner(f: Callable[[X, E], E]) -> E:
            return self.reverse().fold_left(zero)(lambda e, t: f(t, e))

        return inner

    def fold(self, zero: X) -> Callable[[Callable[[X, X], E]], E]:
        """Return the accumulation of the Xlist elements.
        
        Shorthand for fold_left
        """
        return self.fold_left(zero)

    def reduce(self, f: Callable[[X, X], X]) -> X:
        if len(self) <= 0:
            raise IndexError("<reduce> operation not allowed on empty list")
        return self.tail().fold(self.head())(f)
