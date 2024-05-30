from xfp import Xeffect, XFXBranch, Xlist
from ...utils import id
import pytest

def test_xeffect_set_bias():
    input = Xeffect(XFXBranch.LEFT, None, XFXBranch.LEFT)
    actual = input.set_bias(XFXBranch.RIGHT)
    expected = Xeffect(XFXBranch.LEFT, None, XFXBranch.RIGHT)
    
    assert actual == expected
    
    
def test_xeffect_map_left_do():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.LEFT)
    actual = input.map_left(lambda x: x + 2)
    expected = Xeffect(XFXBranch.LEFT, 3, XFXBranch.LEFT)
    
    assert actual == expected

    
def test_xeffect_map_left_pass():
    input = Xeffect(XFXBranch.LEFT, 1, XFXBranch.RIGHT)
    actual = input.map_left(lambda x: x + 2)
    
    assert actual == input
    
    
def test_xeffect_map_right_do():
    input = Xeffect(XFXBranch.RIGHT, 1, XFXBranch.RIGHT)
    actual = input.map_right(lambda x: x + 2)
    expected = Xeffect(XFXBranch.RIGHT, 3, XFXBranch.RIGHT)
    
    assert actual == expected

    
def test_xeffect_map_right_pass():
    input = Xeffect(XFXBranch.RIGHT, 1, XFXBranch.LEFT)
    actual = input.map_right(lambda x: x + 2)
    
    assert actual == input

#Xeffect(XFXBranch.LEFT, Xeffect(XFXBranch.RIGHT, 3, XFXBranch.RIGHT), XFXBranch.LEFT)
#Xeffect(XFXBranch.LEFT, Xeffect(XFXBranch.LEFT, 3, XFXBranch.RIGHT), XFXBranch.LEFT)
#Xeffect(XFXBranch.RIGHT, Xeffect(XFXBranch.RIGHT, 3, XFXBranch.LEFT), XFXBranch.RIGHT)
#Xeffect(XFXBranch.RIGHT, Xeffect(XFXBranch.LEFT, 3, XFXBranch.LEFT), XFXBranch.RIGHT)
 
def test_xeffect_flatten():
    reduce = lambda x: x.value
    combinations = Xlist([
        (Xeffect(XFXBranch.LEFT, Xeffect(XFXBranch.RIGHT, 3, XFXBranch.RIGHT), XFXBranch.RIGHT), id),
        (Xeffect(XFXBranch.LEFT, Xeffect(XFXBranch.RIGHT, 3, XFXBranch.LEFT), XFXBranch.LEFT), reduce),
        (Xeffect(XFXBranch.LEFT, Xeffect(XFXBranch.RIGHT, 3, XFXBranch.LEFT), XFXBranch.RIGHT), id),
        (Xeffect(XFXBranch.LEFT, Xeffect(XFXBranch.LEFT, 3, XFXBranch.RIGHT), XFXBranch.RIGHT), id),
        (Xeffect(XFXBranch.LEFT, Xeffect(XFXBranch.LEFT, 3, XFXBranch.LEFT), XFXBranch.LEFT), reduce),
        (Xeffect(XFXBranch.LEFT, Xeffect(XFXBranch.LEFT, 3, XFXBranch.LEFT), XFXBranch.RIGHT), id),
        (Xeffect(XFXBranch.RIGHT, Xeffect(XFXBranch.RIGHT, 3, XFXBranch.RIGHT), XFXBranch.LEFT), id),
        (Xeffect(XFXBranch.RIGHT, Xeffect(XFXBranch.RIGHT, 3, XFXBranch.RIGHT), XFXBranch.RIGHT), reduce),
        (Xeffect(XFXBranch.RIGHT, Xeffect(XFXBranch.RIGHT, 3, XFXBranch.LEFT), XFXBranch.LEFT), id),
        (Xeffect(XFXBranch.RIGHT, Xeffect(XFXBranch.LEFT, 3, XFXBranch.RIGHT), XFXBranch.LEFT), id),
        (Xeffect(XFXBranch.RIGHT, Xeffect(XFXBranch.LEFT, 3, XFXBranch.RIGHT), XFXBranch.RIGHT), reduce),
        (Xeffect(XFXBranch.RIGHT, Xeffect(XFXBranch.LEFT, 3, XFXBranch.LEFT), XFXBranch.LEFT), id)
    ])
    combinations
    expected = Xlist([1, 2, 3])
    
    assert actual == expected
    

def test_xeffect_flatten_id():
    input = Xlist([1, 2, 3])
    actual = input.flatten()
    
    assert actual == input
    
    
"""   
    def flatten(self) -> "Xeffect[E, E]":
        match self:
            case Xeffect( _, Xeffect(branch, value, in_bias), out_bias) if in_bias == out_bias:
                return Xeffect(branch, value, out_bias)
            case Xeffect(_, Xeffect(_, _, _), _):
                raise TypeError(
                    f"Effect flattening can only work within same bias. Found ${self}"
                )
            case default:  # same bias, either plain value or wrong branch to flatten
                return default

    def flat_map_left(self, f: Callable[[X], E]) -> "Xeffect[E, Y]":
        match self.branch:
            case XFXBranch.LEFT:
                return (
                    Xeffect(self.branch, f(cast(X, self.value)), XFXBranch.LEFT)
                    .flatten()
                    .set_bias(self.bias)
                )
            case XFXBranch.RIGHT:
                return self

    def flat_map_right(self, f: Callable[[Y], E]) -> "Xeffect[X, E]":  
        match self.branch:
            case XFXBranch.RIGHT:
                return (
                    Xeffect(self.branch, f(cast(Y, self.value)), XFXBranch.RIGHT)
                    .flatten()
                    .set_bias(self.bias)
                )
            case XFXBranch.LEFT:
                return self

    def flat_map(self, f: Callable[[X | Y], E]) -> "Xeffect[E, E]":
        match self.bias:
            case XFXBranch.LEFT:
                return self.flat_map_left(f)
            case XFXBranch.RIGHT:
                return self.flat_map_right(f)

    def fold(self, default: E) -> Callable[[Callable[[X | Y], E]], E]:
        def inner(f: Callable[[X | Y], E]) -> E:
            if self.bias == self.branch:
                return f(self.value)
            else:
                return default

        return inner
    
    def get_or_else(self, default: X | Y) -> X | Y:
        return self.fold(default)(id)

    def foreach_left(self, statement: Callable[[X], Any]) -> None:
        match self.branch:
            case XFXBranch.LEFT:
                statement(cast(X, self.value))
            case XFXBranch.RIGHT:
                pass

    def foreach_right(self, statement: Callable[[Y], Any]) -> None:
        match self.branch:
            case XFXBranch.RIGHT:
                statement(cast(Y, self.value))
            case XFXBranch.LEFT:
                pass

    def foreach(self, statement: Callable[[X | Y], E]) -> None:
        match self.bias:
            case XFXBranch.LEFT:
                return self.foreach_left(statement)
            case XFXBranch.RIGHT:
                return self.foreach_right(statement)
                """
