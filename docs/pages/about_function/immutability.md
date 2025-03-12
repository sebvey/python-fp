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


# THE REASSIGN METHOD BREAKS IMMUTABILITY PRINCIPLE
# It mutates the object passed as argument
# What can append when we use it with Xiter instances ?


def reassign(a: A) -> A:
    a.text += "TOUCHED"
    return a


underlying = [A("Foo"), A("Bar")]

# r0 is a first XFP Iterable, on an underlying iterable object
r0 = Xiter(underlying)

# r1 is a new XFP Iterable, constructed from a shallow copy of r0
# -> the underlying iterable is the same
# -> no evaluation of elements is done here
r1 = r0.map(reassign)

# Elements of an Xiter are evaluated when needed, for example when calling
# methods next() / get() / foreach() / take_while() ...

# Below, we cast r1 to a list. Implicitly, the method __list__() is called
# that evaluates each elements

# Before r1 evaluation:
underlying  # -> [A("Foo"), A("Bar")]

# r1 elements evaluation:
list(r1)  # -> [A(text='FooTOUCHED'), A(text='BarTOUCHED')]
underlying  # -> [A(text='FooTOUCHED'), A(text='BarTOUCHED')]

# r0 elements evaluation
# the previous r1 evaluation have modified the underlying iterable
# r0 is not evaluated as we should have expected
list(r0)  # -> [A(text='FooTOUCHED'), A(text='BarTOUCHED')]


# It can be a good practice to enforce immutability to avoid unintentional side effects
# Here we use the frozen property of dataclasses


@dataclass(frozen=True)
class B:
    text: str


def reassign(a: B) -> B:
    a.text += "TOUCHED"
    return a


underlying = [B("Foo"), B("Bar")]
r0 = Xiter(underlying).map(reassign)
r0.to_Xlist()  # -> dataclasses.FrozenInstanceError: cannot assign to field 'text'
``` 
