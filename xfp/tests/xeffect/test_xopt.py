from xfp import Xopt, Xresult, XRBranch


def test_from_optional_lift_some():
    input = 3
    expected = Xopt.Some(3)
    actual = Xopt.from_optional(input)

    assert actual == expected


def test_from_optional_lift_none():
    input = None
    expected = Xopt.Empty
    actual = Xopt.from_optional(input)

    assert actual == expected


def test_Xopt_instantiate_xresult():
    some = Xopt.Some(3)
    empty = Xopt.Empty

    assert isinstance(some, Xresult)
    assert isinstance(empty, Xresult)
    assert some == Xresult(3, XRBranch.RIGHT)
    assert empty == Xresult(None, XRBranch.LEFT)


def test_some_can_be_pattern_match():
    match Xresult(3, XRBranch.RIGHT):
        case Xopt.Some(v):
            assert v == 3
        case _:
            assert False


def test_empty_can_be_pattern_match():
    match Xresult(None, XRBranch.LEFT):
        case Xopt.Empty:
            assert True
        case _:
            assert False


def test_empty_do_not_false_positive():
    match Xresult(Exception("not empty"), XRBranch.LEFT):
        case Xopt.Empty:
            assert False
        case _:
            assert True
