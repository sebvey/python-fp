---
layout: page
title: Collections
permalink: /collections/
nav_order: 98
---

<h1 style="font-weight: bold">Collections</h1>

XFP comes with multiple collection types sharing an homogene API. It means different "how" but similar "what" following the functional paradigm of declarative programming.

```python
from xfp import Xlist, Xiter

Xlist([1, 2, 3]).map(lambda x: x * 2)
Xiter([1, 2, 3]).map(lambda x: x * 2)
```

Despite those two lines declaring the same transformation, the one on Xlist is eager (it is immediately interpreted), while the one on Xiter is lazy (it is interpreted when needed on `next()` calls).  
Look at the specific documentation of each collection type for further information on implementation.

## Common API

### Transforming your data

When using the collection API, you can alter the collection using standard transformations.  
`map` provides a way to apply a transformation on each element of the collection.  
`filter` eliminates keep only elements of a collection that feat the given predicate.  
`flatten` explodes eventual other iterable existing inside the collection.  
`flat_map` combines `map` and `flatten`.  

```python
from xfp import Xlist
(
    Xlist([1, 2, 3])
    .map(lambda x: x * 10)      # Xlist([10, 20, 30])
    .filter(lambda x: x < 25)   # Xlist([10, 20])
    .flat_map(lambda x: [x, x]) # Xlist([10, 10, 20, 20])
)
```

### Accessing your data

Once your transformations are described, you will want to exploit the result of the transformation. 
Every collection is homogene with the standard python collection API. You can indeed still use your favorite utils `len`, `iter` & co.  
However the XFP wrapping provides a few other means.  
`get` is a synonym of `__getitem__`.  
`head` is a synonym of `get(0)`.  
`tail` returns a new collection without the first element (useful in recursion).  
`foreach` applies a procedure on every element without returning anything.  

```python
from xfp import Xlist

Xlist([1, 2, 3]).get(1) # returns 2

def concatenate(xlist: Xlist[int], multiple: int = 1, acc: int = 0) -> int:
    if len(xlist) <= 0:
        return acc
    else:
        return concatenate(xlist.tail(), multiple * 10, acc + xlist.head() * multiple)

concatenate(Xlist([1, 2, 3]))   # returns 321
Xlist([1, 2, 3]).foreach(print) # display every element of the list
```

Note that `get`, `head` and `tail` function also exists in a "_fr" version that returns a LEFT [Xresult](/python-fp/results/) instead of raising an Error on empty list : 

```python
from xfp import Xlist

Xlist([]).head_fr() # Xresult(IndexError(...), XRBranch.LEFT)
```

### Aggregating methods

Aggregation of lists is also facilitated using XFP.  
`fold`, `fold_left` and `fold_right` exist to aggregate a collection into an accumulator, providing its initial state.  
`reduce` is a shorthand for `fold` with the initial accumulator state being set with the list's first element (therefore it fails on empty list. Note that an "_fr" version also exists).  
`min` and `max` are shorthand for `reduce(lambda x, y: x if x < y else y)` (respectively `>`).  

```python
from xfp import Xlist

Xlist([1, 2, 3]).fold(100)(lambda x, y: x + y) # returns 106
Xlist([100, 1, 2, 3]).reduce(lambda x, y: x + y) # returns 106
```

### Copying your collections

Applying a transformation over a collection systematically creates a shallow copy of it.  
`copy` exists as a shorthand for `map(lambda x: x)`. Use it to cleanly tee your collection, independently from the implementation.
`deepcopy` on the other hand will also recursively copy the content of the collections.

```python
from xfp import Xlist
from dataclasses import dataclass

@dataclass
class Wrapper:
    i: int

xlist = Xlist([Wrapper(1)])
shallow_xlist = xlist.copy()
deep_xlist = xlist.deepcopy()

shallow_xlist.get(0).i = 3

print(xlist.get(0))         # Wrapper(3)
print(deep_xlist.get(0))    # Wrapper(1)
```

{: .warning }
Depending on the implementation, `deepcopy` behavior can be tricky. In particular, you may want to read [this about Xiter](/python-fp/collections/xiter#tee-ing-xiter---a-word-about-copying)
