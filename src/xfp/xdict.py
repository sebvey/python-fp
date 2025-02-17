from abc import abstractmethod
from typing import (
    Any,
    Iterator,
    Protocol,
    cast,
    overload,
    runtime_checkable,
)

from xfp import Xlist, Xresult, Xtry, tupled
from collections.abc import Iterable as ABCIterable

from xfp.functions import F1


@runtime_checkable
class ABCDict[Y, X](Protocol):
    @abstractmethod
    def __getitem__(self, key: Y, /) -> X: ...
    @overload
    def get(self, key: Y, /) -> X | None: ...
    @overload
    def get(self, key: Y, default, /) -> Any: ...
    # Mixin methods
    def items(self) -> ABCIterable[tuple[Y, X]]: ...
    def keys(self) -> ABCIterable[Y]: ...
    def values(self) -> ABCIterable[X]: ...
    def __contains__(self, key: object, /) -> bool: ...
    def __eq__(self, other: object, /) -> bool: ...


class Xdict[Y, X]:
    @classmethod
    def from_list(cls, iterable: ABCIterable[tuple[Y, X]]) -> "Xdict[Y, X]":
        """Return a new Xdict built from an iterable.

        The iterable must contain couples of <key, values>. In case of key duplication
        in the parameters list, the last associated value is kept.

        ### Usage

        ```python
            from xfp import Xdict

            xdict = Xdict.from_list([("a", 1), ("b", 2), ("a", 3)])
            assert xdict == Xdict({"a": 3, "b": 2})
        ```
        """
        return cls({k: v for k, v in iterable})

    def __init__(self, dic: ABCDict[Y, X]) -> None:
        """Construct an Xdict from a dict-like.

        Dict-like is defined by the existence of the "items" method.
        """
        self.__data = dict(dic.items())

    def __iter__(self) -> Iterator[tuple[Y, X]]:
        """Return an iterable over the underlying data."""
        return iter(self.items())

    def __len__(self) -> int:
        """Return the length of the underlying data.

        Length of an Xdict is the number of distinct keys.
        """
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

    def __contains__(self, key: Any) -> bool:
        """Return the presence of the key in the xdict keyset."""
        return key in self.keys()

    def __getitem__(self, i: Y) -> X:
        """Alias for get(i).

        Exists to enable [] syntax

        ### Raises

        - IndexError : if the key is not found in the Xdict
        """
        return self.get(i)

    @overload
    def get(self, y: Y, /) -> X:
        """Return the value associated with a given key.

        ### Raises

        - IndexError : if the key is not found in the Xdict
        """
        ...

    @overload
    def get(self, y: Y, default: X, /) -> X:
        """Return the value associated with a given key.

        If the key is not found in the Xdict, return the given default instead.
        """
        ...

    def get(self, *args) -> X:
        """Return the value associated with a given key.

        Implementation for the different `get` methods.
        Should not be called outside of the provided overloaded signatures.

        ### Raises

        - IndexError : if the key is not found in the Xdict and no default is provided
        - AttributeError : if the method is called with an unspecified set of parameters (signature not found in overload)
        """
        match args:
            case [y] if y in self.keys():
                return cast(X, self.__data.get(y))
            case [y]:
                raise IndexError(f"Key not found in Xdict : {y}")
            case [y, default]:
                return self.__data.get(y, default)
            case _:
                raise AttributeError("Wrong set of parameters for <get> method")

    def get_fr(self, y: Y, /) -> Xresult[IndexError, X]:
        """Return the value associated with a given key.

        Wrap the result in an Xtry to catch potential errors.

        ### Returns

        - Xtry.Success : an Xresult containing the value if the key is found
        - Xtry.Failure : with an IndexError if the key is not found

        ### Usage

        ```python
            from xfp import Xdict, Xtry

            match Xdict({"a": 1}).get_fr("b"):
                case Xtry.Success(value):
                    print(f"we found {value} in Xdict")
                case Xtry.Failure(e):
                    print(f"Error: {e}")
        ```
        """
        return cast(Xresult[IndexError, X], Xtry.from_unsafe(lambda: self.get(y)))

    def updated[T](self, key: Y, value: T) -> "Xdict[Y, X | T]":
        """Return a new Xdict, with an updated couple (key: Y, value: E).

        Upsert a new `value` at `key`.

        ### Usage

        ```python
            from xfp import Xdict

            assert Xdict({"a": 1}).updated("b", 2) == Xdict({"a": 1, "b": 2})
            assert Xdict({"a": 1}).updated("a", 2) == Xdict({"a": 2})
        ```
        """
        return self.union(Xdict({key: value}))

    def removed(self, key: Y) -> "Xdict[Y, X]":
        """Return a new Xdict, with the given key deleted.

        Filter the provided key if found.
        No error is raised if the key doesn't exist.

        ### Usage

        ```python
            from xfp import Xdict

            assert Xdict({"a": 1, "b": 2}).removed("b") == Xdict({"a": 1})
            assert Xdict({"a": 1}).removed("b") == Xdict({"a": 1})
        ```
        """
        return self.filter(lambda y, _: y is not key)

    def union[T, U](self, other: ABCDict[U, T]) -> "Xdict[Y | U, X | T]":
        """Return a new Xdict, being the merge of self and a given one.

        Works as if multiple updateds are done successively.
        It means if a key is present in both Xdict, the `other` Xdict has priority.

        ### Usage

        ```python
            from xfp import Xdict

            assert Xdict({"a": 1, "b": 2}).union(Xdict({"a": 3, "c": 4})) == Xdict({"a": 3, "b": 2, "c": 4})
        ```
        """
        return Xdict.from_list(list(self.items()) + list(other.items()))

    def keys(self) -> Xlist[Y]:
        """Return an Xlist of the keys of the Xdict."""
        return Xlist(self.__data.keys())

    def values(self) -> Xlist[X]:
        """Return an Xlist of the values of the Xdict."""
        return Xlist(self.__data.values())

    def items(self) -> Xlist[tuple[Y, X]]:
        """Return an Xlist of the couples (key, value) of the Xdict."""
        return Xlist(self.__data.items())

    def map[T, U](self, f: F1[[Y, X], tuple[U, T]]) -> "Xdict[U, T]":
        """Return a new Xdict, after transformation of the couples (key, value) through `f`.

        Transform each couple with `f`, then recreate an Xdict with the result.
        In case of conflicts in the resulted key set, which value is associated with each key is an unenforced behavior,
        meaning this case should be avoided.
        However, consistency between executions is enforced and the same Xdict will be returned each time.

        ### Usage

        ```python
            from xfp import Xdict

            assert Xdict({"a": 1, "b": 2}).map(lambda y, x: (f"{y}{y}", x * 10)) == Xdict({"aa": 10, "bb": 20})

            collisioned = Xdict({"a": 1, "b": 2}).map(lambda _, x: ("c", x * 10))
            assert collisioned == Xdict({"c": 20}) or collisioned == Xdict({"c": 10}) # but it will always return the same
        ```
        """
        return Xdict.from_list(self.items().map(tupled(f)))

    def map_keys[U](self, f: F1[[Y], U]) -> "Xdict[U, X]":
        """Return a new Xdict, after transformation of the keys through `f`.

        Transform each key with `f`, then recreate an Xdict with the result.
        In case of conflicts in the resulted key set, which value is associated with each key is an unenforced behavior,
        meaning this case should be avoided.
        However, consistency between executions is enforced and the same Xdict will be returned each time.

        ### Usage

        ```python
            from xfp import Xdict

            assert Xdict({"a": 1, "b": 2}).map_keys(lambda y: f"{y}{y}") == Xdict({"aa": 1, "bb": 2})

            collisioned = Xdict({"a": 1, "b": 2}).map(lambda _: "c")
            assert collisioned == Xdict({"c": 2}) or collisioned == Xdict({"c": 1}) # but it will always return the same
        ```
        """
        return self.map(lambda y, x: (f(y), x))

    def map_values[T](self, f: F1[[X], T]) -> "Xdict[Y, T]":
        """Return a new Xdict, after transformation of the values through `f`.

        Transform each value with `f`, then recreate an Xdict with the result.

        ### Usage

        ```python
            from xfp import Xdict

            assert Xdict({"a": 1, "b": 2}).map_values(lambda x: x * 10) == Xdict({"a": 10, "b": 20})
        ```
        """
        return self.map(lambda y, x: (y, f(x)))

    def filter(self, predicate: F1[[Y, X], bool]) -> "Xdict[Y, X]":
        """Return a new Xdict, with the couples not matching the predicate deleted.

        Filter the Xdict couples (key, value) using `predicate`.
        Couples that doesn't match are deleted.

        ### Usage

        ```python
            from xfp import Xdict

            assert Xdict({"a": "a", "b": "c"}).filter(lambda y, x: y == x) == Xdict({"a": "a"})
        ```
        """
        return self.from_list(self.items().filter(tupled(predicate)))

    def filter_keys(self, predicate: F1[[Y], bool]) -> "Xdict[Y, X]":
        """Return a new Xdict, with the couples not matching the predicate deleted.

        Filter the Xdict keys using `predicate`.
        Keys that doesn't match are deleted.

        ### Usage

        ```python
            from xfp import Xdict

            assert Xdict({"a": 1, "b": 20}).filter(lambda y: y in ["a", "c"]) == Xdict({"a": 1})
        ```
        """
        return self.filter(lambda y, _: predicate(y))

    def filter_values(self, predicate: F1[[X], bool]) -> "Xdict[Y, X]":
        """Return a new Xdict, with the couples not matching the predicate deleted.

        Filter the Xdict values using `predicate`.
        Values that doesn't match are deleted.

        ### Usage

        ```python
            from xfp import Xdict

            assert Xdict({"a": 1, "b": 20}).filter(lambda x: x < 10) == Xdict({"a": 1})
        ```
        """
        return self.filter(lambda _, x: predicate(x))

    def foreach(self, statement: F1[[Y, X], Any]) -> None:
        """Do the 'statement' procedure once for each couple (key, value) of the Xdict.

        ### Usage

        ```python
            from xfp import Xdict

            input = Xlist({"a": 1, "b": 2})
            statement = lambda y, x: print(f"This is an element of the dict : ({y}, {x})")
            input.foreach(statement)
            # This is an element of the dict : (a, 1)
            # This is an element of the dict : (b, 2)
        ```
        """
        self.items().foreach(tupled(statement))

    def foreach_keys(self, statement: F1[[Y], Any]) -> None:
        """Do the 'statement' procedure once for each key of the Xdict.

        ### Usage

        ```python
            from xfp import Xdict

            input = Xlist({"a": 1, "b": 2})
            statement = lambda y: print(f"This is a key of the dict : {y}")
            input.foreach_keys(statement)
            # This is a key of the dict : a
            # This is a key of the dict : b
        ```
        """
        return self.foreach(lambda y, _: statement(y))

    def foreach_values(self, statement: F1[[X], Any]) -> None:
        """Do the 'statement' procedure once for each value of the Xdict.

        ### Usage

        ```python
            from xfp import Xdict

            input = Xlist({"a": 1, "b": 2})
            statement = lambda x: print(f"This is a value of the dict : {x}")
            input.foreach_values(statement)
            # This is a value of the dict : 1
            # This is a value of the dict : 2
        ```
        """
        return self.foreach(lambda _, x: statement(x))
