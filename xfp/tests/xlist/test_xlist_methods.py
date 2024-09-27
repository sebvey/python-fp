from xfp import XFXBranch, Xeffect, Xlist, tupled
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


def test_xlist_head_fx():
    input = Xlist([1, 2, 3, 4])
    actual = input.head_fx()
    expected = Xeffect.right(1)

    assert actual == expected


def test_xlist_head__fx_fail():
    input = Xlist([])
    actual = input.head_fx()

    assert isinstance(actual.value, IndexError) and actual.branch == XFXBranch.LEFT


def test_xlist_tail_fx():
    input = Xlist([1, 2, 3, 4])
    actual = input.tail_fx()
    expected = Xeffect.right(Xlist([2, 3, 4]))

    assert actual == expected


def test_xlist_tail_fx_fail():
    input = Xlist([])
    actual = input.tail_fx()

    assert isinstance(actual.value, IndexError) and actual.branch == XFXBranch.LEFT


def test_xlist_head_fx():
    input = Xlist([1, 2, 3, 4])
    actual = input.head_fx()
    expected = Xeffect.right(1)

    assert actual == expected


def test_xlist_head__fx_fail():
    input = Xlist([])
    actual = input.head_fx()

    assert isinstance(actual.value, IndexError) and actual.branch == XFXBranch.LEFT


def test_xlist_tail_fx():
    input = Xlist([1, 2, 3, 4])
    actual = input.tail_fx()
    expected = Xeffect.right(Xlist([2, 3, 4]))

    assert actual == expected


def test_xlist_tail_fx_fail():
    input = Xlist([])
    actual = input.tail_fx()

    assert isinstance(actual.value, IndexError) and actual.branch == XFXBranch.LEFT


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


def test_xlist_reverse():
    input = Xlist([4, 3, -1, 2])
    actual = input.reverse()
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
    input = Xlist([4, 3, -1, 2])
    actual = input.fold(0)(lambda x, y: x + y)
    expected = 8

    assert actual == expected


def test_xlist_reduce():
    input = Xlist([4, 3, -1, 2])
    actual = input.reduce(lambda x, y: x + y)
    expected = 8

    assert actual == expected


def test_xlist_empty_reduce():
    with pytest.raises(IndexError):
        _ = Xlist([]).reduce(lambda x, y: x + y)


def test_xlist_reduce_fx():
    input = Xlist([4, 3, -1, 2])
    actual = input.reduce_fx(lambda x, y: x + y)
    expected = Xeffect.right(8)

    assert actual == expected


def test_xlist_empty_reduce_fx():
    input = Xlist([])
    actual = input.reduce_fx(lambda x, y: x + y)

    assert isinstance(actual.value, IndexError) and actual.branch == XFXBranch.LEFT
    
    
def test_xlist_zip():
    in1 = Xlist([1, 2, 3])
    in2 = Xlist([4, 5])
    assert in1.zip(in2) == Xlist([(1, 4), (2, 5)])
    assert in2.zip(in1) == in1.zip(in2).map(tupled(lambda x, y: (y, x)))
