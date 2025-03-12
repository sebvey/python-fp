---
layout: page
title: Functions
permalink: /functions/
nav_order: 97
---

<h1 style="font-weight: bold">Functions</h1>

Functional programming isn't just about obscure concepts of collection transformations. In its purest form, it begins with working on functions (hint: it's in the name). XFP provides some utils over them to handle functions nicely and conveniently, while keeping the correctness of the typing underneath.

## Currying

{: .further-reading }
Wikipedia defines currying as "the technique of translating a function that takes multiple arguments into a sequence of families of functions, each taking a single argument", but a better explanation can be found [here](https://www.askpython.com/python/examples/currying-in-python). In fact, the full implementation of the curry decorator is the one provided by the author.

XFP provides tooling for partial application of functions. It is useful to pre-parametrize functions given to the collection API (like `map`) in a clean and readable way.

```python
from xfp import Xlist
from xfp.functions import curry2
from typing import Callable

# plain vanilla python equivalent
def vanilla_mult_by(a: int) -> Callable[[int], int]:
    def inner(x: int) -> int:
        return a * x

    return inner

@curry2
def mult_by(a: int, x: int) -> int:
    return a * x

result = mult_by(3)(4)
assert result == 12

Xlist([1, 2, 3]).map(mult_by(3)) # Xlist([3, 6, 9])
```

An equivalent decorator exists for the methods of a class.

```python
from xfp import Xlist
from xfp.functions import curry_method2

class Accumulator:
    def __init__(self):
        self.sum = 0

    @curry_method2
    def mult_and_acc(self, a: int, x: int) -> int:
        self.sum += (r := a * x)
        return r


acc = Accumulator()

Xlist([1, 2, 3]).map(acc.mult_and_acc(3)) # Xlist([3, 6, 9])
assert acc.sum == 18
```

{: .note }
The decorator name is different depending on the number of parameters. For instance, currying `def mul3(a: int, b: int, c: int) -> int: ...` will require the `@curry3` decorator. While a generic `@curry` exists that works with an arbitrary number of parameters, it is recommended to use the specific ones, since `@curry` looses the precise typing of the function.


## Tupling

Another useful functionality for our functions parameters is grouping them into a single tuple parameter. Since our collection API often takes transformation from X to E, it is common to process lists of tuples (for example, created with `zip`) by defining functions of multiple parameters and tupling them on the fly.

```python
from xfp import Xlist
from xfp.functions import tupled2
from typing import Callable

def add(i: int, j: int) -> int:
    return i + j

tupled_add: Callable[[tuple[int, int]], int] = tupled2(add)
assert tupled_add((1, 2)) == 3

# r == Xlist([11, 22, 33])
r = (
    Xlist([1, 2, 3])
    .zip(Xlist([10, 20, 30]))
    .map(tupled(add)) # same as .map(tupled_add)
)
```

{: .note }
Note that the behavior is the same as curry, i.e. a generic `tupled` function exists, but looses the precise type of the values contained in the created tuple.

## Aliases

The native `Callable` representation of a function with vanilla python is already verbose. In combination with multiple currying and the functional paradigms of using functions as parameters and return values, it becomes quite unusable. We provide `Fn` aliases for `Callable`, with n being the level of curryfiction. Starting with `F1` being a plain `Callable` alias. This makes higher order function much more usable.

- Notice the immediate gain as a Callable alias :  

```python
from xfp.functions import F1
from typing import Callable

def concat3(a: int, b: int, c: int) -> str:
    return f"{a}{b}{c}"

alias1: Callable[[int, int, int], str] = concat3
alias2: F1[[int, int, int], str] = concat3

assert alias1(1, 2, 3) == alias2(1, 2, 3)
assert alias2(1, 2, 3) == "123"
```
- However when working with higher order functions it becomes nearly mandatory :  
  
```python
from xfp.functions import F1, F3
from typing import Callable

def concat3(a: int, b: int, c: int): str:
    return f"{a}{b}{c}"

alias1: Callable[[int], Callable[[int], Callable[[int], str]]] = curry3(concat3)
# F3 is just an alias for three chained F1
alias2: F1[[int], F1[[int], F1[[int], str]]] = curry3(concat3)
alias3: F3[[int], [int], [int], str] = curry3(concat3)

assert alias1(1)(2)(3) == alias2(1)(2)(3)
assert alias1(1)(2)(3) == alias3(1)(2)(3)
assert alias2(1)(2)(3) == "123"
```
