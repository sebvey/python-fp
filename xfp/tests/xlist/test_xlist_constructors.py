from xfp import Xlist
import pytest


def test_xlist_from_range():
    input = range(1, 20, 5)
    expected_data = [1, 6, 11, 16]
    actual_data = list(Xlist(input))

    assert actual_data == expected_data


def test_xlist_from_list():
    input = [1, 2, 3, 4]
    expected_data = input
    actual_data = list(Xlist(input))

    assert actual_data == expected_data


def test_xlist_from_tuple():
    input = (4, 3, 2, 1)
    expected_data = [4, 3, 2, 1]
    actual_data = list(Xlist(input))

    assert actual_data == expected_data


def test_xlist_from_generator():
    input = (i**2 for i in (1, 2, 3, 4, 5))
    expected_data = [1, 4, 9, 16, 25]
    actual_data = list(Xlist(input))

    assert actual_data == expected_data


def test_xlist_from_bad_type():
    with pytest.raises(TypeError):
        _ = Xlist(666)  # type: ignore
