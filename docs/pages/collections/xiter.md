---
layout: page
title: Xiter
parent: Collections
permalink: /collections/xiter
nav_order: 2
---

<h1 style="font-weight: bold">Xiter</h1>

This type holds a fully lazy collection. It stores in-memory the transformations, and interprets the whole data flow only when needed, and only the parts that are needed.
It can be seen as a wrapper over Python's `Iterator` type.  
Each transformation creates a new stack of transformation, applying over the same initial elements.  It is of the developer's responsibility to correctly carry on the immutability of the transformations so no side-effect is created upon interpretation. Like the [Xlist](/python-fp/collections/xlist/), you can create a new independent iterator by shallow copying it, or create a whole new set of logical data by deep copying the elements **upon interpretation**.

## Iterator tools

Since Xiter is a lazy collection, it makes it able to store infinite collections, like cycles. It provides a bunch of proxies from itertools to use them efficiently.  
`repeat` creates an Xiter with a unique value repeated infinitely.  
`cycle` creates an Xiter which loops over a given Iterable.

```python
from xfp import Xiter

Xiter.cycle([1, 2, 3]) # Xiter([1, 2, 3, 1, 2, 3, 1, 2, ...])
Xiter.repeat(1)      # Xiter([1, 1, 1, ...])
```

## About evaluation

Xiter is a lazy collection, meaning it doesn't store any value. Evaluation of the transformation is made in a non greedy way. Only the minimum of elements will be evaluated.  
It means if you are asking for the i-th element, every element from 0 to i are going to be interpreted :  

```python

(
    Xiter([1, 2, 3])
    .map(lambda x: x * 2)         # does not evaluate
    .flat_map(lambda x: [x, x])   # does not evaluate
    .get(2)                       # the Xiter logically stores the equivalent of [1, 1, 2, 2, 3, 3]
)                                 # We are requesting this element                      ^
                                  # we evaluate 1 -> (x * 2) -> ([x, x]) and 2 -> (x * 2) -> ([x, x])
                                  # Effectively evaluating the equivalent of [1, 1, 2, 2]
```

## Tee-ing Xiter - a word about copying

Since Xiter is lazy, deepcopy operation is also lazy which can lead to unexpected behavior if the immutability is not strictly followed.  
We strongly advice against directly mutating Xiter elements, however here is a detailled example of how it would reacts in case of need :

```python
from xfp import Xiter
from dataclasses import dataclass

@dataclass
class Wrapper:
    i: int

def unpure(w: Wrapper) -> Wrapper:
    w.i = 10
    return w

xiter = Xiter([1])
mapped_xiter = xiter.map(unpure) # the transformation is encoded, but nothing is executed
deep_xiter = xiter.deepcopy()    # we deep-tee our iterator, expecting it to be fully distinct from xiter and mapped_xiter

print(deep_xiter.get(0))         # prints Wrapper(1) as expected
print(mapped_xiter.get(0))       # prints Wrapper(10) as expected
```

Let's invert our prints : 

```python
from xfp import Xiter
from dataclasses import dataclass

@dataclass
class Wrapper:
    i: int

def unpure(w: Wrapper) -> Wrapper:
    w.i = 10
    return w

xiter = Xiter([1])
mapped_xiter = xiter.map(unpure) # the transformation is encoded, but nothing is executed
deep_xiter = xiter.deepcopy()    # we deep-tee our iterator, expecting it to be fully distinct from xiter and mapped_xiter

print(mapped_xiter.get(0))       # prints Wrapper(10) as expected
print(deep_xiter.get(0))         # prints Wrapper(10) !
```

{: .warning }
Since the deep_xiter is evaluated after the mapped_xiter, the deepcopy is run against the altered input, meaning that although they are two separate instances, the initial state used for copying is incorrect !
