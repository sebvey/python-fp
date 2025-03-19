---
layout: page
title: Xdict
parent: Collections
permalink: /collections/xdict
nav_order: 3
---

<h1 style="font-weight: bold">Xdict</h1>

This type can be seen as a kind of list of couples of (key, value), with a few specificities. Due to its nature of dictionary, navigating between a set of keys and a list of values, only the applicative aspect is kept here (`map`, `filter`, ...), leaving monadic behaviors (`flat_map`) on the side. However, conversion to and from Xlist are available to let the user creates is own semantic when flattening behavior is required.

```python
from xfp import Xdict

xdict = Xdict({"a": 1, "b": 20})
xdict_filtered = xdict.filter_values(lambda x: x < 10)

xdict.foreach_keys(print)          # prints a, b
xdict_filtered.foreach_keys(print) # prints a
```

## Integration with Xlist

Using `items()` and `from_list()` it is possible to convert an Xdict to an Xlist and back. `from_list` automatically handles the keys to ensure unicity, while `items()` creates an Xlist of (key, value) couples in an arbitrary order.  
This enables to lift the Xlist functionalities to the Xdict, while letting the user defines its own edge-cases matching its needs. Here is an example of multiple ways to flatten Xdicts:

- First case: We don't care about key reconciliation
    ```python
    from xfp import Xdict
    from xpf.functions import tupled2, F1

    input = Xdict({"a": 1, "b": 2})
    
    def flat_map[T, U, Y, X](xdict: Xdict[Y, X], f: F1[[Y, X], Xdict[T, U]]) -> Xdict[T, U]:
        return Xdict.from_list(xdict.items().flat_map(tupled2(f)))

    result = flat_map(input, lambda y, x: Xdict({f"{y}{y}": x * x, f"{y}{y}{y}": x * x * x}))
    assert result = Xdict({"aa": 1, "aaa": 1, "bb": 4, "bbb": 8})
    ```
- Second case: The same key may be found accross multiple reduction, we need a custom reconciliation 
    ```python
    from xfp import Xdict
    from xpf.functions import tupled2, F1

    input = Xdict({"a": 1, "b": 2})

    def flat_map[T, U, Y, X](xdict: Xdict[Y, X], f: F1[[Y, X], Xdict[T, U]]) -> Xdict[T, U]:
        fmapped = xdict.items().flat_map(tupled2(f))
        return Xdict.from_list(
            Xlist(set(iter(fmapped.map(tupled2(lambda y, _: y)))))        # we get a list of distinct keys
            .map(lambda x: fmapped.filter(tupled2(lambda y, _: x == y)))  # we split our flat_mapped (key, value) list by keys
            .map(lambda l: l.max(tupled2(lambda _, x: x)))                # we only keep the maximum value for each sublist
        )

    result = flat_map(input, lambda y, x: Xdict({f"{y}{y}": x * x, f"cube": x * x * x}))
    assert result = Xdict({"aa": 1, "cube": 8, "bb": 4})
    ```

## Extended API

Xdict revolves around its (key, value) structure to add indexed search and update methods :
- `updated` returns a new Xdict, with an value upserted.
- `removed` returns a new Xdict, with a couple (key, value) deleted when the key is found.

```python
from xfp import Xdict

assert Xdict({"a": 1}).updated("b", 2) == Xdict({"a": 1, "b": 2})
assert Xdict({"a": 1, "b": 2}).removed("b") == Xdict({"a": 1})
```
