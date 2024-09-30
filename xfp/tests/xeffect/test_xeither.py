from xfp import Xeither, Xeffect, XFXBranch


def test_Xeither_instantiate_xeffect():
    right = Xeither.Right(3)
    left = Xeither.Left(2)

    assert isinstance(right, Xeffect)
    assert isinstance(left, Xeffect)
    assert right == Xeffect(3, XFXBranch.RIGHT)
    assert left == Xeffect(2, XFXBranch.LEFT)


def test_right_can_be_pattern_match():
    match Xeffect(3, XFXBranch.RIGHT):
        case Xeither.Right(v):
            assert v == 3
        case _:
            assert False


def test_left_can_be_pattern_match():
    match Xeffect(2, XFXBranch.LEFT):
        case Xeither.Left(v):
            assert v == 2
        case _:
            assert False
