from typing import Never
from xfp import Xtry, Xresult, XRBranch


def test_from_unsafe_lift_success() -> None:
    def input():
        return 3

    expected = Xtry.Success[int](3)
    actual = Xtry.from_unsafe(input)

    assert actual == expected


def test_from_unsafe_lift_failure() -> None:
    def input():
        raise Exception("fail")

    actual = Xtry.from_unsafe(input)

    assert isinstance(actual.value, Exception)


def test_safed_lift_success() -> None:
    @Xtry.safed
    def actual():
        return 3

    expected = Xtry.Success[int](3)

    assert actual() == expected


def test_safed_lift_failure() -> None:
    @Xtry.safed
    def actual():
        raise Exception("fail")

    assert isinstance(actual().value, Exception)


def test_Xtry_instantiate_xresult() -> None:
    success = Xtry.Success[int](3)
    failure = Xtry.Failure[Exception](Exception("fail"))

    assert isinstance(success, Xresult)
    assert isinstance(failure, Xresult)
    assert success == Xresult[Never, int](3, XRBranch.RIGHT)
    assert failure.branch == XRBranch.LEFT


def test_success_can_be_pattern_match() -> None:
    match Xresult[Never, int](3, XRBranch.RIGHT):
        case Xtry.Success(v):
            assert v == 3
        case _:
            assert False


def test_failure_can_be_pattern_match() -> None:
    match Xresult[Exception, Never](Exception("fail"), XRBranch.LEFT):
        case Xtry.Failure(e):
            assert isinstance(e, Exception) and e.args[0] == "fail"
        case _:
            assert False


def test_empty_do_not_false_positive() -> None:
    match Xresult[None, Never](None, XRBranch.LEFT):
        case Xtry.Failure(_):
            assert False
        case _:
            assert True
