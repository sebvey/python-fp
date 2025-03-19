from dataclasses import dataclass
import itertools
from typing import Never

import pytest
from xfp import XRBranch, Xeither, Xiter, Xlist
from xfp.functions import tupled2
from xfp.xresult._xresult import Xresult


def compare[X](actual: Xiter[X], expected: Xiter[X]) -> bool:
    for i, j in zip(actual.copy(), expected.copy()):
        if i != j:
            return False
    return True


def test_xiter__init__not_iterable() -> None:
    with pytest.raises(TypeError):
        Xiter(123)  # type: ignore


def test_xiter__repr__defined() -> None:
    assert repr(Xiter([1, 2, 3])).startswith("<list_iterator")


def test_xiter_copy() -> None:
    r1 = Xiter([1, 2, 3])
    r2 = r1.copy()
    assert next(r1) == 1
    assert next(r2) == 1


def test_xiter_copy_is_shallow() -> None:
    @dataclass
    class A:
        text: str

    r1 = Xiter([A("hello")])
    r2 = r1.copy()

    value1 = next(r1)
    value2 = next(r2)
    value1.text = "world"
    assert value2.text == value1.text


def test_xiter_deepcopy() -> None:
    r1 = Xiter([1, 2, 3])
    r2 = r1.deepcopy()
    assert next(r1) == 1
    assert next(r2) == 1


def test_xiter_get() -> None:
    assert Xiter.cycle(Xiter([1, 2, 3])).get(4) == 2


def test_xiter_deepcopy_is_deep() -> None:
    @dataclass
    class A:
        text: str

    r1 = Xiter([A("hello")])
    r2 = r1.deepcopy()
    value1 = next(r1)
    value2 = next(r2)

    value1.text = "world"
    assert value2.text == "hello"


def test_xiter_head() -> None:
    input = Xiter([1, 2, 3])
    assert input.head() == 1
    assert input.head() == 1
    assert next(input) == 1


def test_xiter_head_fail() -> None:
    with pytest.raises(IndexError):
        Xiter([]).head()


def test_xiter_head_fr() -> None:
    input = Xiter([1, 2, 3])
    assert input.head_fr() == Xeither.Right(1)
    assert input.head_fr() == Xeither.Right(1)
    assert next(input) == 1


def test_xiter_head_fr_fail() -> None:
    input = Xiter[int]([])
    actual = input.head_fr()
    assert isinstance(actual.value, IndexError) and actual.branch == XRBranch.LEFT


def test_xiter_appended():
    input = Xiter([1])
    actual = input.appended(2)
    expected = Xiter([1, 2])
    assert compare(actual, expected)


def test_xiter_prepended():
    input = Xiter([1])
    actual = input.prepended(2)
    expected = Xiter([2, 1])
    assert compare(actual, expected)


def test_xiter_filter() -> None:
    input = Xiter(range(1, 10, 1))
    actual = input.filter(lambda x: x % 2 == 0)
    expected = Xiter(range(2, 10, 2))

    assert compare(actual, expected)


def test_xiter_flat_map() -> None:
    input = Xiter([1, 2])
    actual = input.flat_map(lambda x: [x, x**2])
    expected = Xiter([1, 1, 2, 4])

    assert compare(actual, expected)


def test_xiter_flatten() -> None:
    input = Xiter([[1, 2], [3]])
    actual = input.flatten()
    expected = Xiter([1, 2, 3])

    assert compare(actual, expected)


def test_xiter_map() -> None:
    input = Xiter([1, 2, 3, 4])
    actual = input.map(lambda x: (x - 1) * -1)
    expected = Xiter([0, -1, -2, -3])

    assert compare(actual, expected)


def test_xiter_slice_does_not_copy() -> None:
    input = Xiter(range(0, 10))
    _ = input.slice(4)
    assert compare(input, Xiter(range(0, 10)))


def test_xiter_slice_stop_arg() -> None:
    input = Xiter(range(0, 10))
    assert compare(input.slice(4), Xiter(range(4)))


def test_xiter_slice_stop_none_arg() -> None:
    input = Xiter(range(0, 10))
    assert compare(input.slice(None), Xiter(range(0, 10)))


def test_xiter_slice_start_stop_args() -> None:
    input = Xiter(range(0, 10))
    assert compare(input.slice(1, 7), Xiter(range(1, 7)))


def test_xiter_slice_start_stop_step_args() -> None:
    input = Xiter(range(0, 100))
    assert compare(input.slice(1, 60, 3), Xiter(range(1, 60, 3)))


def test_xiter_slice_start_stop_step_none_args() -> None:
    input = Xiter(range(0, 100))
    assert compare(input.slice(None, None, None), Xiter(range(0, 100)))


def test_xiter_slice_too_many_args() -> None:
    with pytest.raises(TypeError):
        Xiter([1]).slice(1, 2, 3, 4)  # type: ignore


def test_xiter_tail() -> None:
    input = Xiter([1, 2, 3])
    assert compare(input.tail(), Xiter([2, 3]))
    assert compare(input.tail(), Xiter([2, 3]))
    assert compare(input, Xiter([1, 2, 3]))


def test_xiter_tail_fail() -> None:
    with pytest.raises(IndexError):
        Xiter([]).tail()


def test_xiter_tail_fr() -> None:
    input = Xiter([1, 2, 3])
    assert compare(input.tail(), Xiter([2, 3]))
    assert compare(input.tail(), Xiter([2, 3]))
    assert compare(input, Xiter([1, 2, 3]))


def test_xiter_tail_fr_fail() -> None:
    input = Xiter[int]([])
    actual = input.tail_fr()
    assert isinstance(actual.value, IndexError) and actual.branch == XRBranch.LEFT


def test_xiter_fold() -> None:
    input = Xiter(["b", "c"])
    actual = input.fold("a", lambda acc, el: acc + el)
    expected = "abc"

    assert actual == expected


def test_xiter_reduce() -> None:
    input = Xiter([4, 3, -1, 2])
    actual = input.reduce(lambda x, y: x + y)
    expected = 8

    assert actual == expected


def test_xiter_empty_reduce() -> None:
    with pytest.raises(IndexError):
        _ = Xiter[int]([]).reduce(lambda x, y: x + y)


def test_xiter_reduce_fr() -> None:
    input = Xiter([4, 3, -1, 2])
    actual = input.reduce_fr(lambda x, y: x + y)
    expected: Xresult[Never, int] = Xeither.Right(8)

    assert actual == expected


def test_xiter_empty_reduce_fr() -> None:
    input = Xiter[int]([])
    actual = input.reduce_fr(lambda x, y: x + y)

    assert isinstance(actual.value, IndexError) and actual.branch == XRBranch.LEFT


def test_xiter_min() -> None:
    input = Xiter([4, 3, -1, 2])
    actual = input.min()
    expected = -1

    assert actual == expected


def test_xiter_min_fr() -> None:
    input = Xiter[int]([])
    actual = input.min_fr()

    assert isinstance(actual.value, ValueError)


def test_xiter_max() -> None:
    input = Xiter([4, 3, -1, 2])
    actual = input.max()
    expected = 4

    assert actual == expected


def test_xiter_max_fr() -> None:
    input = Xiter[int]([])
    actual = input.max_fr()

    assert isinstance(actual.value, ValueError)


def test_xiter_takewhile() -> None:
    input = Xiter(itertools.count(0, 1))
    actual = input.takewhile(lambda x: x < 10)
    expected = Xiter(range(10))
    assert compare(actual, expected)
    assert next(input) == 0


def test_xiter_takeuntil() -> None:
    input = Xiter(itertools.count(0, 1))
    actual = input.takeuntil(lambda x: x >= 10)
    expected = Xiter(range(10))
    assert compare(actual, expected)
    assert next(input) == 0


def test_xiter_to_xlist() -> None:
    input = Xiter(range(5))
    assert input.to_Xlist() == Xlist([0, 1, 2, 3, 4])
    assert next(input) == 0


def test_xiter_zip() -> None:
    in1 = Xiter([1, 2, 3])
    in2 = Xiter([4, 5])
    assert compare(in1.zip(in2), Xiter([(1, 4), (2, 5)]))
    assert compare(in2.zip(in1), in1.zip(in2).map(tupled2(lambda x, y: (y, x))))
