from inspect import signature
from functools import partial
from typing import TypeVar, ParamSpec, cast, Concatenate, Callable, Any

A = TypeVar("A")
P = ParamSpec("P")
T = TypeVar("T")
Self = TypeVar("Self")

# Element type alias
type E = Any
type Unused = None


def id[E](e: E) -> E:
    return e


def curry(f: Callable[Concatenate[A, P], T]) -> Callable[[A], Any]:
    if len(signature(f).parameters) == 1:
        return cast(Callable[[A], T], f)
    else:

        def g(x: A) -> Callable:
            return curry(cast(Callable, partial(f, x)))

        return g


def curry_method(f: Callable[Concatenate[Self, A, P], T]) -> Callable[[Self, A], Any]:
    if len(signature(f).parameters) == 2:
        return cast(Callable[[Self, A], T], f)
    else:

        def g(self: Self, x: A) -> Callable:
            return curry(cast(Callable, partial(f, self, x)))

        return g


def tupled(f: Callable[..., T]) -> Callable[[tuple], T]:
    def g(t: tuple) -> T:
        return f(*t)

    return g
