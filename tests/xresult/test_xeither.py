from xfp import Xeither, Xresult, XRBranch


def test_Xeither_instantiate_xresult():
    right = Xeither.Right(3)
    left = Xeither.Left(2)

    assert isinstance(right, Xresult)
    assert isinstance(left, Xresult)
    assert right == Xresult(3, XRBranch.RIGHT)
    assert left == Xresult(2, XRBranch.LEFT)


def test_right_can_be_pattern_match():
    match Xresult(3, XRBranch.RIGHT):
        case Xeither.Right(v):
            assert v == 3
        case _:
            assert False


def test_left_can_be_pattern_match():
    match Xresult(2, XRBranch.LEFT):
        case Xeither.Left(v):
            assert v == 2
        case _:
            assert False
