---
layout: page
title: Immutability
parent: Functional programming in Python
permalink: /about_function/immutability
nav_order: 1
---
<h1 style="font-weight: bold">Immutability</h1>

The immutability paradigm isn't strongly anchored into Python practices, which makes enforcing it difficult. It can indeed gives a false sentiment of security at best, and conflicts with existing libraries at worst. We have chosen to sometimes only make assumption of immutability and delegate to the developer the responsability of enforcing it. 
```python
from xfp import Xiter
from dataclasses import dataclass

@dataclass
class A:
    text: str


def reassign(a):
    a.text = a.text + "world"
    return a


r0 = Xiter([A("hello")])
r1 = r0.map(reassign)
r2 = r0.deepcopy()

# calling r2 before r1 makes value2.text = hello
value2 = next(r2)
value1 = next(r1)

assert value2.text == "hello"
``` 

```python
from xfp import Xiter
from dataclasses import dataclass

@dataclass
class A:
    text: str


def reassign(a):
    a.text = a.text + "world"
    return a


r0 = Xiter([A("hello")])
r1 = r0.map(reassign)
r2 = r0.deepcopy()
# inverting the two calls changes the value of value2.text
value1 = next(r1)
value2 = next(r2)

assert value2.text == "helloworld"
``` 