from abc import ABC, abstractmethod
from typing import Any, Generator, override

from xfp import Xeither, Xresult, Xiter, Xlist, curry, tupled, Xopt
from xfp.functions import tupled2
from xfp.xresult import XRBranch, XresultError


class Sink[T](ABC):
    @abstractmethod
    def fill(self, value: T) -> None:
        pass


class Appender[T](Sink[T]):
    def __init__(self) -> None:
        self.value: list[T] = []

    @override
    def fill(self, value: T) -> None:
        self.value.append(value)


@curry
def forced_side_effect[T](sink: Sink[T], value: T) -> T:
    sink.fill(value)
    return value


def test_xlist_eager() -> None:
    sink = Appender[Any]()
    eager_value = forced_side_effect(sink)
    assert sink.value == []
    r1 = Xlist([1, 2, 3]).map(lambda x: eager_value(x))
    assert sink.value == [1, 2, 3]
    _ = r1.flat_map(lambda x: eager_value([eager_value(x)]))
    assert sink.value == [1, 2, 3, 1, [1], 2, [2], 3, [3]]


def test_xiter_lazy() -> None:
    sink = Appender[Any]()
    eager_value = forced_side_effect(sink)
    assert sink.value == []
    r1 = Xiter([1, 2, 3]).map(lambda x: eager_value(x))
    assert sink.value == []
    r2 = r1.flat_map(lambda x: eager_value([x, eager_value(x * 10)]))
    assert next(r2) == 1
    assert sink.value == [1, 10, [1, 10]]
    assert next(r2) == 10
    r2.foreach(print)
    assert sink.value == [1, 10, [1, 10], 2, 20, [2, 20], 3, 30, [3, 30]]
    r2.foreach(print)
    assert sink.value == [1, 10, [1, 10], 2, 20, [2, 20], 3, 30, [3, 30]]


def test_xiter_consumation() -> None:
    r1 = Xiter([1, 2, 3])
    r2 = r1.map(lambda x: x * x)
    assert next(r1) == 1
    assert next(r2) == 1
    r3 = r2.map(lambda x: x * x)
    assert next(r1) == 2
    assert next(r1) == 3
    assert next(r2) == 4
    assert next(r3) == 16
    assert next(r3) == 81
    assert next(r2) == 9


def test_xiter_from_generator() -> None:
    def gen() -> Generator[int, Any, None]:
        for i in [1, 2, 3]:
            yield i

    r1 = Xiter(gen())
    r2 = r1.map(lambda x: x * x)
    assert next(r1) == 1
    assert next(r2) == 1
    r3 = r2.map(lambda x: x * x)
    assert next(r1) == 2
    assert next(r1) == 3
    assert next(r2) == 4
    assert next(r3) == 16
    assert next(r3) == 81
    assert next(r2) == 9


def test_xiter_to_xlist_should_eval() -> None:
    sink = Appender[int]()
    eager_value = forced_side_effect(sink)
    assert sink.value == []
    r1 = Xiter([1, 2, 3]).map(lambda x: eager_value(x))
    assert sink.value == []
    _ = Xlist(r1)
    assert sink.value == [1, 2, 3]


def test_xiter_infinite_iterator_works_fine() -> None:
    sink = Appender[int]()
    eager_value = forced_side_effect(sink)
    assert sink.value == []
    r1 = Xiter.repeat(1)
    r2 = Xiter.cycle(Xiter([1, 2, 3]))
    r3 = r1.zip(r2).map(tupled2(lambda x, y: eager_value(x + y)))
    assert sink.value == []
    assert r3[3] == 2
    assert sink.value == [2, 3, 4, 2]


def test_xiter_fizzbuzz() -> None:
    def notify(frequency: int, text: str) -> Xiter[Xresult[None, str]]:
        raw = [Xopt.Empty] * (frequency - 1)
        raw.append(Xopt.Some(text))
        return Xiter([Xopt.Empty]).chain(Xiter.cycle(raw))

    def concat(
        first: Xresult[None, str], second: Xresult[None, str]
    ) -> Xresult[None, str]:
        match (first, second):
            case (Xopt.Some(ll), Xopt.Some(rr)):
                return Xopt.Some(ll + rr)
            case (_, Xopt.Empty):
                return first
            case _:
                return second

    f = notify(3, "fizz").zip(notify(5, "buzz")).map(tupled(concat))

    assert f[3] == Xeither.Right("fizz")
    assert f[5] == Xeither.Right("buzz")
    assert f[15] == Xeither.Right("fizzbuzz")


def test_for_comprehension_pass() -> None:
    result: Xresult[XresultError, int] = Xresult.fors(
        lambda: [x + y for x, y in zip(Xeither.Right[int](1), Xeither.Right[int](2))]
    )

    assert result == Xeither.Right(3)


def test_for_comprehension_fail() -> None:
    result: Xresult[XresultError, int] = Xresult.fors(
        lambda: [
            x + y
            for x, y in zip(Xeither.Right[int](1), Xresult[int, int](2, XRBranch.LEFT))
        ]
    )

    assert result == Xeither.Left(XresultError(Xresult(2, XRBranch.LEFT)))
