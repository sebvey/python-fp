from typing import Any, Never
from xfp import Xopt, Xresult, XRBranch


def test_from_optional_lift_some() -> None:
    input = 3
    expected = Xopt.Some[int](3)
    actual: Xresult[None, int] = Xopt.from_optional(input)

    assert actual == expected


def test_from_optional_lift_none() -> None:
    input = None
    expected: Xresult[None, Never] = Xopt.Empty
    actual: Xresult[None, Any] = Xopt.from_optional(input)

    assert actual == expected


def test_Xopt_instantiate_xresult() -> None:
    some = Xopt.Some[int](3)
    empty: Xresult[None, Never] = Xopt.Empty

    assert isinstance(some, Xresult)
    assert isinstance(empty, Xresult)
    assert some == Xresult[Never, int](3, XRBranch.RIGHT)
    assert empty == Xresult[None, Never](None, XRBranch.LEFT)


def test_some_can_be_pattern_match() -> None:
    match Xresult[Never, int](3, XRBranch.RIGHT):
        case Xopt.Some(v):
            assert v == 3
        case _:
            assert False


def test_empty_can_be_pattern_match() -> None:
    match Xresult[None, Never](None, XRBranch.LEFT):
        case Xopt.Empty:
            assert True
        case _:
            assert False


def test_empty_do_not_false_positive() -> None:
    match Xresult[Exception, Never](Exception("not empty"), XRBranch.LEFT):
        case Xopt.Empty:
            assert False
        case _:
            assert True
