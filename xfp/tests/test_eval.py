from abc import ABC, abstractmethod
from typing import override

from xfp import Xiter, Xlist, curry


class Sink[T](ABC):
    def __init__(self) -> None:
        self.value = None

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


def test_xlist_eager():
    sink = Appender()
    eager_value = forced_side_effect(sink)
    assert sink.value == []
    r1 = Xlist([1, 2, 3]).map(lambda x: eager_value(x))
    assert sink.value == [1, 2, 3]
    _ = r1.flat_map(lambda x: eager_value([eager_value(x)]))
    assert sink.value == [1, 2, 3, 1, [1], 2, [2], 3, [3]]


def test_xiter_lazy():
    sink = Appender()
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


def test_xiter_consumation():
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
