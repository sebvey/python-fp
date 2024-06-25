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

    def __str__(self) -> str:
        """Return the string representation of the underlying data"""
        return str(self.__data)

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

        Usage:
        input = Xlist([1, 2, 3])
        f = lambda el: el*el
        assert input.map(f) == Xlist([f(1), f(2), f(3)]) # == Xlist([1, 4, 9])
        """
        return Xlist([f(el) for el in self])

    def filter(self, predicate: Callable[[X], bool]) -> "Xlist[X]":
        """Return a new Xlist containing only the elements for which predicate is True.

        Usage:
        input = Xlist([1, 2, 3, 4])
        predicate = lambda el: el % 2 == 0
        assert input.filter(predicate) == Xlist([2, 4]) # keep only even numbers
        """
        return Xlist([el for el in self if predicate(el)])

    def foreach(self, statement: Callable[[X], Any]) -> None:
        """Do the 'statement' procedure once for each element of the Xlist.

        Usage:
        input = Xlist([1, 2, 3])
        statement = lambda el: println(f"This is an element of the list : ${el}")
        input.foreach(statement)
        # This is an element of the list : 1
        # This is an element of the list : 2
        # This is an element of the list : 3
        """
        [statement(e) for e in self]

    def flatten(self) -> "Xlist[E]":
        """Return a new Xlist with one less level of nest.

        Usage:
        assert Xlist.flatten([1, 2, 3]) == Xlist([1, 2, 3])
        assert Xlist.flatten([[1, 2], [3]]) == Xlist([1, 2, 3])
        assert Xlist.flatten([[1, 2], 3]) == Xlist([1, 2, 3])
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

        Exists as homogenisation with Xeffect.flat_map
        Usage:
        assert Xlist([1, 2, 3]).flat_map(lambda x: Xlist([4, 5]).map(lambda y: (x, y))) == Xlist([(1, 4), (2, 4), (3, 4), (1, 5), (2, 5), (3, 5)])
        """
        return self.map(f).flatten()

    def min(self, key: Callable[[X], E] = id) -> X:
        """Return the smallest element of the Xlist given the key criteria.

        Keyword Arguments:
        key (default id) -- the function which extrapolate a sortable from the elements of the list
        Usage:
        input = Xlist(["ae", "bd", "cc"])
        assert input.min() == "ae"
        assert input.min(lambda x: x[-1]) == "cc"
        """
        return min(self, key=key)

    def max(self, key: Callable[[X], E] = id) -> X:
        """Return the biggest element of the Xlist given the key criteria.

        Keyword Arguments:
        key (default id) -- the function which extrapolate a sortable from the elements of the list

        Usage:
        input = Xlist(["ae", "bd", "cc"])
        assert input.max() == "cc"
        assert input.max(lambda x: x[-1]) == "ae"
        """
        return max(self, key=key)

    def sorted(self, key: Callable[[X], E] = id, reverse: bool = False) -> "Xlist[X]":
        """Return a new Xlist containing the same elements sorted given the key criteria.

        Keyword Arguments:
        key (default id)        -- the function which extrapolate a sortable from the elements of the list
        reverse (default False) -- should we sort ascending (False) or descending (True)
        Usage:
        input = Xlist(["bd", "ae", "cc"])
        assert input.sorted() == Xlist(["ae", "bd", "cc"])
        assert input.sorted(lambda x: x[-1]) == Xlist(["cc", "bd", "ae"])
        assert input.sorted(lambda x: x[-1], reverse = True) == Xlist(["ae", "bd", "cc"])
        """
        return Xlist(sorted(self, key=key, reverse=reverse))

    def reverse(self) -> "Xlist[X]":
        """Return a new Xlist containing the same elements in the reverse order."""
        data: list[X] = self.__data.copy()
        data.reverse()
        return Xlist(data)

    def fold_left(self, zero: E) -> Callable[[Callable[[E, X], E]], E]:
        """Return the accumulation of the Xlist elements.

        Uses a custom accumulator (zero, f) to aggregate the elements of the Xlist
        Initialize the accumulator with the zero value
        Then from the first to the last element, compute accumulator(n+1) using f, accumulator(n) and self.data[n], such as:
        accumulator(n+1) = f(accumulator(n), self.data[n])
        Return the last state of the accumulator
        Keyword Arguments:
        zero -- initial state of the accumulator
        f    -- accumulation function, compute the next state of the accumulator
        Usage:
        assert Xlist([1, 2, 3]).fold_left(0)(lambda x, y: x + y) == 6
        assert Xlist([1, 2, 3]).fold_left(10)(lambda x, y: x + y) == 16
        assert Xlist(["1", "2", "3"]).fold_left("")(lambda x, y: x + y) == "123"
        assert Xlist([]).fold_left(0)(lambda x, y: x + y) == 0
        """

        def inner(f: Callable[[E, X], E]) -> E:
            acc: E = zero
            for e in self:
                acc = f(acc, e)
            return acc

        return inner

    def fold_right(self, zero: E) -> Callable[[Callable[[X, E], E]], E]:
        """Return the accumulation of the Xlist elements.

        Uses a custom accumulator (zero, f) to aggregate the elements of the Xlist
        Initialize the accumulator with the zero value
        Then from the last to the first element, compute accumulator(n+1) using f, accumulator(n) and self.data[n], such as:
        accumulator(n+1) = f(accumulator(n), self.data[n])
        Return the last state of the accumulator
        Keyword Arguments:
        zero -- initial state of the accumulator
        f    -- accumulation function, compute the next state of the accumulator
        Usage:
        assert Xlist([1, 2, 3]).fold_right(0)(lambda x, y: x + y) == 6
        assert Xlist([1, 2, 3]).fold_right(10)(lambda x, y: x + y) == 16
        assert Xlist(["1", "2", "3"]).fold_right("")(lambda x, y: x + y) == "321"
        assert Xlist([]).fold_right(0)(lambda x, y: x + y) == 0
        """

        def inner(f: Callable[[X, E], E]) -> E:
            return self.reverse().fold_left(zero)(lambda e, t: f(t, e))

        return inner

    def fold(self, zero: X) -> Callable[[Callable[[X, X], E]], E]:
        """Return the accumulation of the Xlist elements.

        Shorthand for fold_left
        """
        return self.fold_left(zero)

    def reduce(self, f: Callable[[X, X], X]) -> X:
        """Return the accumulation of the Xlist elements using the first element as the initial state of accumulation.

        Raise:
        IndexError -- when the Xlist is empty
        Keyword Arguments:
        f -- accumulation function, compute the next state of the accumulator
        Usage:
        assert Xlist([1, 2, 3]).reduce(lambda x, y: x + y) == 6
        assert Xlist(["1", "2", "3"]).reduce(lambda x, y: x + y) == "321"
        with pytest.raises(IndexError):
            Xlist([]).reduce(lambda x, y: x + y)
        """
        if len(self) <= 0:
            raise IndexError("<reduce> operation not allowed on empty list")
        return self.tail().fold(self.head())(f)
