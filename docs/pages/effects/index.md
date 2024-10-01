---
layout: page
title: Effects
permalink: /results/
nav_order: 99
---

<h1 style="font-weight: bold">Effects</h1>

{: .further-reading }
Effects handling in XFP are based on the functional pattern [railway oriented programming](https://naveenkumarmuguda.medium.com/railway-oriented-programming-a-powerful-functional-programming-pattern-ab454e467f31)

As you may see in [Functional Programming in Python](/python-fp/functional_programming/), a good practice is to encode semantic in your funtions signatures. XFP provides a unique way to encode different semantics at once through its Xresult type. 

## What is an effect

In the functional world, an effect is the description of an operation interacting with the outside world, thus making the function unpure. It ranges from I/O operation to mutating something not in in the function scope. Its consequences (overly simplified) result often in something that is not a value (much like `None` or raising `Exception`).

```python
import pandas as pd
import math
# read_csv raises FileNotFoundError when phantom_file does not exist
df = pd.read_csv("phantom_file.csv") 

# sqrt return None when i < 0. The function is partial
def sqrt(i):
    if i >= 0:
        return math.sqrt(i)
```

One of the property of the function is that it should always return a value. Therefore effects break the functional paradigm and should be handled. Python handles them with keywords, however we will handle them with values, introducing the Xresult XFP type to **catch the output of an effect**.

```python
import pandas as pd
# Python handles errors with try/except
try:
    df = pd.read_csv("phantom_file.csv")
except Exception as e:
    print(e)
```

## Mecanisms

### Type Structure

`Xresult[Y, X]` can be seen as a collection of one unique element `value`, being either of type Y or X. It always holds a `branch` attribute as a semaphore of which type between X or Y is used. branch is a value of the `XFXBranch` enumeration, equals to `XFXBranch.LEFT` if the `value` is a Y or a `XFXBranch.RIGHT` if the value is a LEFT.  

```python
from xfp import Xresult, XFXBranch
from typing import Any
import math

result1: Xresult[Any, int] = Xresult(3, XFXBranch.RIGHT)
result2: Xresult[str, Any] = Xresult("abc", XFXBranch.LEFT)

# this is a preview of the added semantic of returning an Xresult
def partial_sqrt(i: int) -> Xresult[str, int]:
    if i >= 0:
        return Xresult(math.sqrt(i), XFXBranch.RIGHT)
    else:
        return Xresult(f"{i} cannot be square rooted", XFXBranch.LEFT)
```

{: .note }
You may find the partial_sqrt error handling tedious. This is completely normal since this is an overview of the plain effect handling in xfp. For more information about quality of lifes with effects, see [Wrapping Python](/python-fp/results/wrapping_python)

### API

#### As a collection

As a collection with a unique element, Xresults are homogene with the [Collections](/python-fp/collections/) API. It means you can process the value of an Xresult using the standard `map`, `flat_map`, `filter` & co functions. However to take the branch into account, each function is divided into a "_left" and a "_right" version, each one either applying the transformation if the branch corresponds, or being a go-through otherwise.

```python
from xfp import Xresult, XFXBranch

(
    Xresult(1, XFXBranch.RIGHT)
    .map_right(lambda x: x + 10)                            # XFXBranch(1 + 10, XFXBranch.RIGHT) because result is a RIGHT
    .map_left(lambda y: y * 20)                             # go-through because result is a RIGHT
    .flat_map_right(lambda x: Xresult(2, XFXBranch.LEFT))   # Xresult(2, XFXBranch.LEFT) because the initial result is a RIGHT
    .foreach_right(print)                                   # prints 2
)
```

{: .note }
For convenience, Xresult is right-biased, meaning a non-suffixed function is a proxy for a "_right" one. For example `my_xresult.map(f)` is the same as `my_xresult.map_right(f)`

### Result branching

The collection API provides a bunch of functions that operate on the value to either transform it or to return a new Xresult (`map`, `flat_map`). However the Xresult itself add some functionalities to work on its branch (and optionally change its value). As before, every function exists in a left and right version, the unsuffixed one being a synonym for the right.  
`filter` returns a new Xresult being the opposite branch with the value holding a default error if the predicate is not met.  
`recover_with` is an alias over flat_map, on the opposite branch (`recover_with_left` = `flat_map_right`). It is meant to try to re-shift to the current bias.
`recover` holds a similar semantic as `recover_with` but with an absolute recovery method.

```python
from xfp import Xresult, XFXBranch

(
    Xresult("I am the wrong value", XFXBranch.LEFT)  # Let's encode an 'error' in the LEFT path
    .recover_right(lambda err_msg: len(err_msg))     # Xresult(20, XFXBranch.RIGHT)
    .filter_right(lambda size: size < 5)             # Xresult(XresultError(...), XFXBranch.LEFT)
)
```

## Integrate Semantic

In [Result branching](#result-branching) we started implying the existence of a "right" path, and an "error" one. While you should remember the mechanical behavior of Xresult, it is of equal importance to understand how it adds semantic to your code. It is a common and a good practice to encode a main value on one side, and a value representing the side effect on the other side.

```python

from xfp import Xresult, XFXBranch
from typing import Any
import math

# Xresult[None, X] formally encodes 
def partial_sqrt(i: int) -> Xresult[None, int]:
    if i >= 0:
        return Xresult(math.sqrt(i), XFXBranch.RIGHT)
    else:
        return Xresult(None, XFXBranch.LEFT)

```

## Xeither, Xtry, Xopt