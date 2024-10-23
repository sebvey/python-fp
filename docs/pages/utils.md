---
layout: page
title: Utils
permalink: /utils/
nav_order: 100
---

<h1 style="font-weight: bold">Utils</h1>

Functional programming isn't just about obscure concepts of collection transformations. In its purest form, it begins with working on functions (hint: it's in the name). With python being a little light over functions transformations, XFP provides a few more utils over them.

## Currying

{: .further-reading }
Wikipedia defines currying as "the technique of translating a function that takes multiple arguments into a sequence of families of functions, each taking a single argument", but a better explanation can be found [here](https://www.askpython.com/python/examples/currying-in-python). In fact, the full implementation of the curry decorator is the one provided by the author.

XFP provides tooling for partial application of functions. It is useful to pre-parametrize functions given to the collection API (like `map`) in a clean and readable way.

```python
from xfp import curry, Xlist
from typing import Callable

# plain vanilla python equivalent
def vanilla_mult_by(a: int) -> Callable[[int], int]:
    def inner(x: int) -> int:
        return a * x

    return inner

@curry
def mult_by(a: int, x: int) -> int:
    return a * x

result = mult_by(3)(4)
assert result == 12

Xlist([1, 2, 3]).map(mult_by(3)) # Xlist([3, 6, 9])
```

An equivalent decorator exists for the methods of a class.

```python
from xfp import curry_method, Xlist

class Accumulator:
    def __init__(self):
        self.sum = 0

    @curry_method
    def mult_and_acc(self, a: int, x: int) -> int:
        self.sum += (r := a * x)
        return r


acc = Accumulator()

Xlist([1, 2, 3]).map(acc.mult_and_acc(3)) # Xlist([3, 6, 9])
assert acc.sum == 18
```

## Tupling

Another useful functionalities for our functions parameters is grouping them into a single tuple parameter. Since our collection API often takes transformation from X to E, it is common to process lists of tuples (for example, created with `zip`) by defining functions of multiple parameters and tupling them on the fly.

```python
from xfp import Xlist, tupled
from typing import Callable

def add(i: int, j: int) -> int:
    return i + j

tupled_add: Callable[[tuple[int, int]], int] = tupled(add)
assert tupled_add((1, 2)) == 3

# r == Xlist([11, 22, 33])
r = (
    Xlist([1, 2, 3])
    .zip(Xlist([10, 20, 30]))
    .map(tupled(add)) # same as .map(tupled_add)
)
```
