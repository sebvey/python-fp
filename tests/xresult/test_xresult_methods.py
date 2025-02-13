from typing import Never
from xfp import (
    Xresult,
    XRBranch,
    XresultError,
    Xeither,
)


def test_xresult_map_left_do() -> None:
    input = Xresult[int, Never](1, XRBranch.LEFT)
    actual: Xresult[int, Never] = input.map_left(lambda x: x + 2)
    expected: Xresult[int, Never] = Xresult(3, XRBranch.LEFT)

    assert actual == expected


def test_xresult_map_left_pass() -> None:
    input = Xresult[Never, int](1, XRBranch.RIGHT)
    actual: Xresult[int, int] = input.map_left(lambda x: x + 2)

    assert actual == input


def test_xresult_map_right_do() -> None:
    input = Xresult[Never, int](1, XRBranch.RIGHT)
    actual: Xresult[Never, int] = input.map_right(lambda x: x + 2)
    expected: Xresult[Never, int] = Xresult(3, XRBranch.RIGHT)

    assert actual == expected


def test_xresult_map_right_pass() -> None:
    input = Xresult[int, Never](1, XRBranch.LEFT)
    actual: Xresult[int, int] = input.map_right(lambda x: x + 2)

    assert actual == input


def test_xresult_flatten() -> None:
    assert Xeither.Left(1).flatten() == Xeither.Left(1)
    assert Xeither.Right(Xeither.Right(3)).flatten() == Xeither.Right(3)
    assert Xeither.Right(Xeither.Left(1)).flatten() == Xeither.Left(1)


def test_xresult_flat_map_left_do() -> None:
    input = Xresult[int, Never](1, XRBranch.LEFT)
    actual: Xresult[int, Never] = input.flat_map_left(
        lambda x: Xresult[int, Never](x + 2, XRBranch.LEFT)
    )
    expected = Xresult[int, Never](3, XRBranch.LEFT)

    assert actual == expected


def test_xresult_flat_map_left_do_but_fail() -> None:
    input = Xresult[int, Never](1, XRBranch.LEFT)
    actual: Xresult[Never, None] = input.flat_map_left(
        lambda x: Xresult[Never, None](None, XRBranch.RIGHT)
    )
    expected: Xresult[Never, None] = Xresult(None, XRBranch.RIGHT)

    assert actual == expected


def test_xresult_flat_map_left_pass() -> None:
    input = Xresult[Never, int](1, XRBranch.RIGHT)
    actual: Xresult[int, int] = input.flat_map_left(
        lambda x: Xresult[int, Never](x + 2, XRBranch.LEFT)
    )

    assert actual == input


def test_xresult_flat_map_right_do() -> None:
    input = Xresult[Never, int](1, XRBranch.RIGHT)
    actual: Xresult[Never, int] = input.flat_map_right(
        lambda x: Xresult[Never, int](x + 2, XRBranch.RIGHT)
    )
    expected = Xresult[Never, int](3, XRBranch.RIGHT)

    assert actual == expected


def test_xresult_flat_map_right_do_but_fail() -> None:
    input = Xresult[Never, int](1, XRBranch.RIGHT)
    actual: Xresult[None, Never] = input.flat_map_right(
        lambda x: Xresult[None, Never](None, XRBranch.LEFT)
    )
    expected = Xresult[None, Never](None, XRBranch.LEFT)

    assert actual == expected


def test_xresult_flat_map_right_pass() -> None:
    input = Xresult[int, Never](1, XRBranch.LEFT)
    actual: Xresult[int, int] = input.flat_map_right(
        lambda x: Xresult[Never, int](x + 2, XRBranch.RIGHT)
    )

    assert actual == input


def test_xresult_fold_value() -> None:
    input = Xresult[Never, int](1, XRBranch.RIGHT)
    actual: int = input.fold(36)(lambda x: x + 2)
    expected = 3

    assert actual == expected


def test_xresult_fold_default() -> None:
    input = Xresult[int, Never](1, XRBranch.LEFT)
    actual: int = input.fold(36)(lambda x: x + 2)
    expected = 36

    assert actual == expected


def test_xresult_get_or_else_value() -> None:
    input = Xresult[Never, int](1, XRBranch.RIGHT)
    actual: int = input.get_or_else(36)
    expected = 1

    assert actual == expected


def test_xresult_get_or_else_default() -> None:
    input = Xresult[int, Never](1, XRBranch.LEFT)
    actual: int = input.get_or_else(36)
    expected = 36

    assert actual == expected


def test_xresult_recover_with_left_pass() -> None:
    input = Xresult[int, Never](1, XRBranch.LEFT)
    actual: Xresult[int, int] = input.recover_with_left(
        lambda _: Xresult[Never, int](2, XRBranch.RIGHT)
    )

    assert actual == input


def test_xresult_recover_with_left_recover() -> None:
    input = Xresult[Never, int](1, XRBranch.RIGHT)
    expected = Xresult[Never, int](2, XRBranch.RIGHT)
    actual: Xresult[Never, int] = input.recover_with_left(lambda _: expected)

    assert actual == expected


def test_xresult_recover_with_right_pass() -> None:
    input = Xresult[Never, int](1, XRBranch.RIGHT)
    actual: Xresult[Never, int] = input.recover_with_right(
        lambda _: Xresult[Never, int](2, XRBranch.RIGHT)
    )

    assert actual == input


def test_xresult_recover_with_right_recover() -> None:
    input = Xresult[int, Never](1, XRBranch.LEFT)
    expected = Xresult[Never, int](2, XRBranch.RIGHT)
    actual: Xresult[Never, int] = input.recover_with_right(lambda _: expected)

    assert actual == expected


def test_xresult_recover_left_pass() -> None:
    input = Xresult[int, Never](1, XRBranch.LEFT)
    actual: Xresult[int, Never] = input.recover_left(lambda _: 2)

    assert actual == input


def test_xresult_recover_left_do() -> None:
    input = Xresult[Never, int](1, XRBranch.RIGHT)
    expected = Xresult[int, Never](2, XRBranch.LEFT)
    actual: Xresult[int, Never] = input.recover_left(lambda _: 2)

    assert actual == expected


def test_xresult_recover_right_pass() -> None:
    input = Xresult[Never, int](1, XRBranch.RIGHT)
    actual: Xresult[Never, int] = input.recover_right(lambda _: 2)

    assert actual == input


def test_xresult_recover_right_do() -> None:
    input = Xresult[int, Never](1, XRBranch.LEFT)
    expected = Xresult[Never, int](2, XRBranch.RIGHT)
    actual: Xresult[Never, int] = input.recover_right(lambda _: 2)

    assert actual == expected


def test_xresult_filter_left_pass() -> None:
    input = Xresult[Never, int](3, XRBranch.RIGHT)
    actual: Xresult[Never, int | XresultError[Never, int]] = input.filter_left(
        lambda x: x > 10
    )
    print(actual)
    print(input)

    assert actual == input


def test_xresult_filter_left_do() -> None:
    input = Xresult[int, Never](3, XRBranch.LEFT)
    expected = Xresult[Never, XresultError[int, Never]](
        XresultError(input), XRBranch.RIGHT
    )
    actual: Xresult[int, XresultError[int, Never]] = input.filter_left(lambda x: x > 10)

    assert actual == expected


def test_xresult_filter_right_pass() -> None:
    input = Xresult[int, Never](3, XRBranch.LEFT)
    actual: Xresult[int | XresultError[int, Never], Never] = input.filter_right(
        lambda x: x > 10
    )

    assert actual == input


def test_xresult_filter_right_do() -> None:
    input = Xresult[Never, int](3, XRBranch.RIGHT)
    expected = Xresult[XresultError[Never, int], Never](
        XresultError(input), XRBranch.LEFT
    )
    actual: Xresult[XresultError[Never, int], int] = input.filter_right(
        lambda x: x > 10
    )

    assert actual == expected
