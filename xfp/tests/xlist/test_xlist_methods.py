from xfp import XRBranch, Xlist, tupled, Xeither
import pytest


def test_xlist_head():
    input = Xlist([1, 2, 3, 4])
    actual = input.head()
    expected = 1

    assert actual == expected


def test_xlist_head_fail():
    with pytest.raises(IndexError):
        Xlist([]).head()


def test_xlist_tail():
    input = Xlist([1, 2, 3, 4])
    actual = input.tail()
    expected = Xlist([2, 3, 4])

    assert actual == expected


def test_xlist_tail_fail():
    with pytest.raises(IndexError):
        Xlist([]).tail()


def test_xlist_head_fr():
    input = Xlist([1, 2, 3, 4])
    actual = input.head_fr()
    expected = Xeither.Right(1)

    assert actual == expected


def test_xlist_head__fr_fail():
    input = Xlist([])
    actual = input.head_fr()

    assert isinstance(actual.value, IndexError) and actual.branch == XRBranch.LEFT


def test_xlist_tail_fr():
    input = Xlist([1, 2, 3, 4])
    actual = input.tail_fr()
    expected = Xeither.Right(Xlist([2, 3, 4]))

    assert actual == expected


def test_xlist_tail_fr_fail():
    input = Xlist([])
    actual = input.tail_fr()

    assert isinstance(actual.value, IndexError) and actual.branch == XRBranch.LEFT


def test_xlist_map():
    input = Xlist([1, 2, 3, 4])
    actual = input.map(lambda x: (x - 1) * -1)
    expected = Xlist([0, -1, -2, -3])

    assert actual == expected


def test_xlist_flatten():
    input = Xlist([[1, 2], [3]])
    actual = input.flatten()
    expected = Xlist([1, 2, 3])

    assert actual == expected


def test_xlist_flatten_id():
    input = Xlist([1, 2, 3])
    actual = input.flatten()

    assert actual == input


def test_xlist_flatten_mixed():
    input = Xlist([[1, 2], 3])
    actual = input.flatten()
    expected = Xlist([1, 2, 3])

    assert actual == expected


def test_xlist_flat_map():
    input = Xlist([1, 2])
    actual = input.flat_map(lambda x: [x, x**2])
    expected = Xlist([1, 1, 2, 4])

    assert actual == expected


def test_xlist_filter():
    input = Xlist(range(1, 10, 1))
    actual = input.filter(lambda x: x % 2 == 0)
    expected = Xlist(range(2, 10, 2))

    assert actual == expected


def test_xlist_sorted():
    input = Xlist([4, 3, 1, 2])
    actual = input.sorted()
    expected = Xlist([1, 2, 3, 4])

    assert actual == expected


def test_xlist_reversed():
    input = Xlist([4, 3, -1, 2])
    actual = input.reversed()
    expected = Xlist([2, -1, 3, 4])

    assert actual == expected


def test_xlist_min():
    input = Xlist([4, 3, -1, 2])
    actual = input.min()
    expected = -1

    assert actual == expected


def test_xlist_max():
    input = Xlist([4, 3, -1, 2])
    actual = input.max()
    expected = 4

    assert actual == expected


def test_xlist_fold():
    input = Xlist(["b", "c"])
    actual = input.fold("a")(lambda x, y: x + y)
    expected = "abc"

    assert actual == expected


def test_xlist_fold_right():
    input = Xlist(["c", "b"])
    actual = input.fold_right("a")(lambda x, y: x + y)
    expected = "abc"

    assert actual == expected


def test_xlist_reduce():
    input = Xlist([4, 3, -1, 2])
    actual = input.reduce(lambda x, y: x + y)
    expected = 8

    assert actual == expected


def test_xlist_empty_reduce():
    with pytest.raises(IndexError):
        _ = Xlist([]).reduce(lambda x, y: x + y)


def test_xlist_reduce_fr():
    input = Xlist([4, 3, -1, 2])
    actual = input.reduce_fr(lambda x, y: x + y)
    expected = Xeither.Right(8)

    assert actual == expected


def test_xlist_empty_reduce_fr():
    input = Xlist([])
    actual = input.reduce_fr(lambda x, y: x + y)

    assert isinstance(actual.value, IndexError) and actual.branch == XRBranch.LEFT


def test_xlist_zip():
    in1 = Xlist([1, 2, 3])
    in2 = Xlist([4, 5])
    assert in1.zip(in2) == Xlist([(1, 4), (2, 5)])
    assert in2.zip(in1) == in1.zip(in2).map(tupled(lambda x, y: (y, x)))
