from typing import Never
from xfp import XRBranch, Xlist, Xeither
import pytest

from xfp.functions import tupled2
from xfp.xresult import Xresult


def test_xlist_head() -> None:
    input = Xlist([1, 2, 3, 4])
    actual = input.head()
    expected = 1

    assert actual == expected


def test_xlist_head_fail() -> None:
    with pytest.raises(IndexError):
        Xlist[Never]([]).head()


def test_xlist_tail() -> None:
    input = Xlist([1, 2, 3, 4])
    actual = input.tail()
    expected = Xlist([2, 3, 4])

    assert actual == expected


def test_xlist_tail_fail() -> None:
    with pytest.raises(IndexError):
        Xlist[Never]([]).tail()


def test_xlist_head_fr() -> None:
    input = Xlist([1, 2, 3, 4])
    actual = input.head_fr()
    expected: Xeither.Right[int] = Xeither.Right(1)

    assert actual == expected


def test_xlist_head__fr_fail() -> None:
    input = Xlist[Never]([])
    actual: Xresult[Exception, Never] = input.head_fr()

    assert isinstance(actual.value, IndexError) and actual.branch == XRBranch.LEFT


def test_xlist_tail_fr() -> None:
    input = Xlist([1, 2, 3, 4])
    actual = input.tail_fr()
    expected: Xeither.Right[list[int]] = Xeither.Right(Xlist([2, 3, 4]))

    assert actual == expected


def test_xlist_tail_fr_fail() -> None:
    input = Xlist[Never]([])
    actual = input.tail_fr()

    assert isinstance(actual.value, IndexError) and actual.branch == XRBranch.LEFT


def test_xlist_appended():
    input = Xlist([1])
    actual = input.appended(2)
    expected = Xlist([1, 2])
    assert actual == expected


def test_xlist_prepended():
    input = Xlist([1])
    actual = input.prepended(2)
    expected = Xlist([2, 1])
    assert actual == expected


def test_xlist_inserted():
    input = Xlist([1, 3, 4, 5, 6])
    actual = input.inserted(2, 2)
    expected = Xlist([1, 3, 2, 4, 5, 6])
    assert actual == expected


def test_xlist_map() -> None:
    input = Xlist([1, 2, 3, 4])
    actual = input.map(lambda x: (x - 1) * -1)
    expected = Xlist([0, -1, -2, -3])

    assert actual == expected


def test_xlist_flatten() -> None:
    input = Xlist([[1, 2], [3]])
    actual = input.flatten()
    expected = Xlist([1, 2, 3])

    assert actual == expected


def test_xlist_flat_map() -> None:
    input = Xlist([1, 2])
    actual = input.flat_map(lambda x: [x, x**2])
    expected = Xlist([1, 1, 2, 4])

    assert actual == expected


def test_xlist_filter() -> None:
    input = Xlist(range(1, 10, 1))
    actual = input.filter(lambda x: x % 2 == 0)
    expected = Xlist(range(2, 10, 2))

    assert actual == expected


def test_xlist_sorted() -> None:
    input = Xlist([4, 3, 1, 2])
    actual = input.sorted()
    expected = Xlist([1, 2, 3, 4])

    assert actual == expected


def test_xlist_reversed() -> None:
    input = Xlist([4, 3, -1, 2])
    actual = input.reversed()
    expected = Xlist([2, -1, 3, 4])

    assert actual == expected


def test_xlist_min() -> None:
    input = Xlist([4, 3, -1, 2])
    actual = input.min()
    expected = -1

    assert actual == expected


def test_xlist_min_fr() -> None:
    input = Xlist[int]([])
    actual = input.min_fr()

    assert isinstance(actual.value, ValueError)


def test_xlist_max() -> None:
    input = Xlist([4, 3, -1, 2])
    actual = input.max()
    expected = 4

    assert actual == expected


def test_xlist_max_fr() -> None:
    input = Xlist[int]([])
    actual = input.max_fr()

    assert isinstance(actual.value, ValueError)


def test_xlist_fold() -> None:
    input = Xlist(["b", "c"])
    actual = input.fold("a", lambda acc, el: acc + el)
    expected = "abc"

    assert actual == expected


def test_xlist_fold_curried() -> None:
    input = Xlist(["b", "c"])
    actual = input.fold("a")(lambda acc, el: acc + el)
    expected = "abc"

    assert actual == expected


def test_xlist_fold_left() -> None:
    input = Xlist(["b", "c"])
    actual = input.fold("a", lambda acc, el: acc + el)
    expected = "abc"

    assert actual == expected


def test_xlist_fold_left_curried() -> None:
    input = Xlist(["b", "c"])
    actual = input.fold_left("a")(lambda acc, el: acc + el)
    expected = "abc"

    assert actual == expected


def test_xlist_fold_right() -> None:
    input = Xlist(["c", "b"])
    actual = input.fold_right("a", lambda el, acc: acc + el)
    expected = "cba"

    assert actual == expected


def test_xlist_fold_right_curried() -> None:
    input = Xlist(["c", "b"])
    actual = input.fold_right("a")(lambda el, acc: acc + el)
    expected = "cba"

    assert actual == expected


def test_xlist_reduce() -> None:
    input = Xlist([4, 3, -1, 2])
    actual = input.reduce(lambda x, y: x + y)
    expected = 8

    assert actual == expected


def test_xlist_empty_reduce() -> None:
    with pytest.raises(IndexError):
        _ = Xlist[int]([]).reduce(lambda x, y: x + y)


def test_xlist_reduce_fr() -> None:
    input = Xlist([4, 3, -1, 2])
    actual = input.reduce_fr(lambda x, y: x + y)
    expected: Xresult[Never, int] = Xeither.Right(8)

    assert actual == expected


def test_xlist_empty_reduce_fr() -> None:
    input = Xlist[int]([])
    actual = input.reduce_fr(lambda x, y: x + y)

    assert isinstance(actual.value, IndexError) and actual.branch == XRBranch.LEFT


def test_xlist_zip() -> None:
    in1 = Xlist([1, 2, 3])
    in2 = Xlist([4, 5])
    assert in1.zip(in2) == Xlist([(1, 4), (2, 5)])
    assert in2.zip(in1) == in1.zip(in2).map(tupled2(lambda x, y: (y, x)))
