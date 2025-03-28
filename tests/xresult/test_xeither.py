from typing import Never
from xfp import Xeither, Xresult, XRBranch


def test_Xeither_instantiate_xresult() -> None:
    right = Xeither.Right[int](3)
    left = Xeither.Left[int](2)

    assert isinstance(right, Xresult)
    assert isinstance(left, Xresult)
    assert right == Xresult[Never, int](3, XRBranch.RIGHT)
    assert left == Xresult[int, Never](2, XRBranch.LEFT)


def test_right_can_be_pattern_match() -> None:
    match Xresult[Never, int](3, XRBranch.RIGHT):
        case Xeither.Right(v):
            assert v == 3
        case _:
            assert False


def test_left_can_be_pattern_match() -> None:
    match Xresult[int, Never](2, XRBranch.LEFT):
        case Xeither.Left(v):
            assert v == 2
        case _:
            assert False
