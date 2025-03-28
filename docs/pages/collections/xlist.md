---
layout: page
title: Xlist
parent: Collections
permalink: /collections/xlist
nav_order: 1
---

<h1 style="font-weight: bold">Xlist</h1>

This type is a simple wrapper over Python `list` type.
It represents a finite collection, fully stored in-memory, with each transformation creating a new in-memory view of the whole list. However each copy is shallow and it is of the developer's responsibility to correctly carry on the immutability of the structure.

```python
from xfp import Xlist
from dataclasses import dataclass

@dataclass
class Wrapper:
    i: int

xlist = Xlist([Wrapper(1), Wrapper(2)])
xlist_filtered = xlist.filter(lambda w: w.i == 1)

xlist.foreach(print) # prints Wrapper(1), Wrapper(2)

xlist_filtered.get(0).i = 4

xlist.foreach(print) # prints Wrapper(4), Wrapper(2)
```

## Extended API

Due to its finite nature, Xlist implements more functionalities relative to reorganizing elements within the array.  
`reversed` returns a new Xlist, with the elements inverted.
`sorted` returns a new Xlist, with the elements sorted (eventually by a custom key).

```python
from xfp import Xlist
from dataclasses import dataclass

@dataclass
class Wrapper:
    i: int

assert Xlist([1, 2, 3]).reversed() == Xlist([3, 2, 1])
assert Xlist([Wrapper(2), Wrapper(1)]).sorted(lambda w: w.i) == Xlist([Wrapper(1), Wrapper(2)])
```
