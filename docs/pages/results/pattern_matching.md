---
layout: page
title: Pattern Matching
parent: Effects
permalink: /results/pattern_matching
nav_order: 1
---

<h1 style="font-weight: bold">Pattern Matching</h1>

The strong typing paradigm of functional languages allows for powerful conditional checks over the types of each values. However Python only implements a very light version of Pattern Matching. the [Xeither, Xopt, Xtry](/python-fp/results/#xeither-xtry-xopt) creates a unique opportunity to capitalize over this simple yet useful functionality. In their metaclass, all of those types resolves to an Xresult, which means they can all be pattern matched conjointly.

## Extracting values

The main usage of Pattern matching is to check the outcome of an Xresult and extract its value at the same time.

```python
from xfp import Xeffect, Xtry

previous_result: Xeffect[Exception, str] = Xtry.Success("everything's right") # mock a previous result here

match previous_result:
    case Xtry.Success(value):
        print(value)
    case Xtry.Failure(e):
        print("Something's wrong")
```

This can be assimilated to the Python try/except pattern, but on a more generalized level. Where the try/except is limited to errors, side effects decriptions can be encoded under any type of value, depending on your need. In this example, we can cleanly handle a multiple-exception effect :

```python
from xfp import Xeffect, Xeither
from typing import Any

previous_result: Xeffect[list[Exception], Any] = Xeither.Left([Exception("e1"), Exception(["e2"])]) # mock a previous result here

match previous_result:
    case Xeither.Right(value):
        print(value)
    case Xeither.Left([e1, *others]):
        print(f"Something's wrong, the first wrong thing is {e1}")
```

## More examples

Since Xtry, Xeither, Xopt all resolves to an Xresult, they can be used interchangeably :

```python
from xfp import Xeffect, Xtry, Xopt

previous_result: Xeffect[Exception, str] = Xtry.Success("everything's right") # mock a previous result here

match previous_result:
    case Xopt.Some(value):
        print(value)
    case Xtry.Failure(e):
        print("Something's wrong")
```

The plain Xresult type can also be used in pattern matching :

```python
from xfp import Xeffect, XFXBranch

previous_result: Xeffect[Exception, str] = Xtry.Success("everything's right") # mock a previous result here

match previous_result:
    case Xresult(value, XFXBranch.RIGHT):
        print(value)
    case Xresult(e, XFXBranch.LEFT):
        print("Something's wrong")
```